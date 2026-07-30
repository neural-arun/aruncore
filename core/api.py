import os
import json
import io
import asyncio
import requests
import queue
import threading
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from core.agent import (
    init_agent,
    RollingMemory,
    queue_debug_event,
    queue_maybe_notify_arun,
    run_pre_escalation,
    queue_chat_history_to_telegram,
)

_GLOBAL_VECTORSTORE = None
_GLOBAL_BM25 = None
_GLOBAL_COMPRESSOR = None

_task_queue = queue.Queue()


def _background_worker():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while True:
        try:
            task = _task_queue.get()
            if task is None:
                break
            func, args, kwargs = task
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"[BACKGROUND WORKER ERROR] Failed in {func.__name__}: {e}")
            finally:
                _task_queue.task_done()
        except Exception as outer_e:
            print(f"[BACKGROUND WORKER FATAL] Queue fetch failed: {outer_e}")


worker_thread = threading.Thread(target=_background_worker, daemon=True)
worker_thread.start()


def _submit_background_task(name: str, func, *args, **kwargs) -> bool:
    try:
        _task_queue.put((func, args, kwargs))
        print(f"[BACKGROUND] {name}: Task queued.")
        return True
    except Exception as e:
        print(f"[BACKGROUND ERROR] Failed to queue {name}: {e}")
        return False


def load_static_context() -> Tuple[str, str]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(base_dir, "data", "static", "public_profile.md")
    rules_path = os.path.join(base_dir, "data", "static", "rules_of_engagement.md")

    profile_content = ""
    rules_content = ""

    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_content = f.read()

    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_content = f.read()

    return profile_content, rules_content


def _safe_truncate(text: str, limit: int = 1500) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."


def _is_truthy_env(val: Optional[str], default: bool = True) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _is_telegram_debug_enabled() -> bool:
    return _is_truthy_env(os.getenv("TELEGRAM_DEBUG_ENABLED"), default=True)


def _get_telegram_target(debug: bool = False, alert: bool = False) -> Tuple[Optional[str], Optional[str]]:
    if alert:
        token = os.getenv("TELEGRAM_ALERT_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ALERT_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
        return token, chat_id
    if debug:
        token = os.getenv("TELEGRAM_DEBUG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_DEBUG_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
        return token, chat_id

    return os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")


def _chunk_text(text: str, limit: int = 2200) -> List[str]:
    cleaned = (text or "").strip() or "(empty)"
    parts: List[str] = []
    remaining = cleaned

    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < int(limit * 0.5):
            split_at = remaining.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit

        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].lstrip()

    if remaining:
        parts.append(remaining)

    return parts or ["(empty)"]


def _send_telegram_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    max_attempts: int = 3,
    delivery_label: str = "default",
    retry_sleep_seconds: float = 1.0,
) -> str:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()
    session.verify = False

    chunks = _chunk_text(text)
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks, 1):
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        sent_chunk = False
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            try:
                res = session.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json=payload,
                    timeout=10,
                )
                if res.status_code == 200 and res.json().get("ok"):
                    sent_chunk = True
                    break
                else:
                    last_error = f"HTTP {res.status_code}: {res.text}"
            except Exception as e:
                last_error = str(e)

            if attempt < max_attempts:
                import time
                time.sleep(retry_sleep_seconds)

        if not sent_chunk and parse_mode == "HTML":
            fallback_payload = {
                "chat_id": chat_id,
                "text": f"[{delivery_label}] (Plain Text Fallback {idx}/{total_chunks})\n{chunk}",
                "disable_web_page_preview": True,
            }
            try:
                res = session.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json=fallback_payload,
                    timeout=10,
                )
                if res.status_code == 200 and res.json().get("ok"):
                    sent_chunk = True
            except Exception as e:
                last_error = f"Fallback error: {e}"

        if not sent_chunk:
            print(f"[TELEGRAM:{delivery_label}] FAILED chunk {idx}/{total_chunks}: {last_error}")
            return f"FAILED: {last_error}"

    print(f"[TELEGRAM:{delivery_label}] SUCCESS")
    return "SUCCESS: message delivered."


# Initialize the ArunCore Engine
try:
    print("Initializing ArunCore API Backend...")
    main_llm, prompt, default_memory, tools = init_agent()

    global_tool_map = {t.name: t for t in tools}

    print("API Backend Initialized Successfully.")
except Exception as e:
    print(f"Failed to initialize backend: {e}")
    raise e

app = FastAPI(title="ArunCore API", description="Stateful Agentic Backend for Arun Yadav's Digital Twin.")

# Enable CORS for external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SESSION MANAGEMENT ===
active_sessions: Dict[str, RollingMemory] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if req.session_id not in active_sessions:
        summary_llm = ChatOpenAI(temperature=0.0, model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"))
        active_sessions[req.session_id] = RollingMemory(summary_llm=summary_llm)

    memory = active_sessions[req.session_id]

    async def generate_response():
        thoughts = []
        try:
            queue_debug_event(
                "user_message",
                req.message,
                {"channel": "api", "session_id": req.session_id},
            )

            yield json.dumps({"type": "status", "content": "Analyzing request & retrieving context..."}) + "\n"
            thoughts.append("Analyzing request & retrieving context...")

            pre_escalation = run_pre_escalation(req.message, global_tool_map)
            if pre_escalation and pre_escalation.get("escalate"):
                yield json.dumps({"type": "status", "content": "Triggering instant Telegram alert..."}) + "\n"
                thoughts.append("Triggering instant Telegram alert...")
                queue_maybe_notify_arun(
                    user_input=req.message,
                    reason=pre_escalation.get("reason"),
                    channel="api",
                    session_id=req.session_id,
                )

            scratchpad = []
            max_iterations = 5
            iterations = 0
            max_search_limit = 3
            search_count = 0
            final_response = ""
            executed_tools = []
            retrieved_chunks = []

            while iterations < max_iterations:
                messages = prompt.format_messages(
                    running_summary=memory.running_summary,
                    chat_history=memory.get_messages(),
                    input=req.message,
                    agent_scratchpad=scratchpad,
                )

                ai_msg = await asyncio.to_thread(main_llm.invoke, messages)

                if ai_msg.tool_calls:
                    scratchpad.append(ai_msg)
                    for tc in ai_msg.tool_calls:
                        tool_name = tc["name"]
                        tool_args = tc.get("args", {})

                        status_msg = "Searching Arun's knowledge base..." if tool_name == "search_arun_knowledge" else \
                                     "Sending notification to Arun..." if tool_name == "notify_arun" else \
                                     f"Executing {tool_name}..."

                        yield json.dumps({"type": "status", "content": status_msg}) + "\n"
                        thoughts.append(status_msg)
                        executed_tools.append(f"{tool_name}({tool_args})")

                        if tool_name == "search_arun_knowledge":
                            search_count += 1

                        if search_count > max_search_limit:
                            tool_result = f"Search limit reached ({max_search_limit}). Finalizing based on existing context."
                        else:
                            tool_func = global_tool_map.get(tool_name)
                            tool_result = await asyncio.to_thread(tool_func.invoke, tool_args)

                        if tool_name == "search_arun_knowledge" and tool_result:
                            retrieved_chunks.append(str(tool_result)[:1000])

                        scratchpad.append({
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tc["id"],
                            "content": str(tool_result)[:2000],
                        })
                    iterations += 1
                else:
                    yield json.dumps({"type": "status", "content": "Synthesizing final response..."}) + "\n"
                    thoughts.append("Synthesizing final response...")

                    full_reply = ""
                    for chunk in main_llm.stream(messages):
                        if chunk.content:
                            full_reply += chunk.content
                            yield json.dumps({"type": "token", "content": chunk.content}) + "\n"
                            await asyncio.sleep(0.005)

                    final_response = full_reply
                    break

            if not final_response:
                final_response = "I encountered a processing limit. How else can I help?"

            memory.add_interaction(req.message, final_response)

            queue_chat_history_to_telegram(
                session_id=req.session_id,
                user_input=req.message,
                assistant_response=final_response,
                thoughts=thoughts,
                tool_calls=executed_tools,
                retrieved_chunks=retrieved_chunks,
            )

            yield json.dumps({
                "type": "final",
                "reply": final_response,
                "thoughts": thoughts,
                "session_id": req.session_id,
            }) + "\n"

        except Exception as err:
            err_msg = f"API Error: {str(err)}"
            yield json.dumps({"type": "error", "content": err_msg}) + "\n"

    return StreamingResponse(generate_response(), media_type="application/x-ndjson")


@app.post("/tts")
async def tts_endpoint(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY missing.")

        clean_snippet = (
            req.text
            .replace("*", "")
            .replace("#", "")
            .replace("`", "")
            .replace("\n", " ")
            [:1000]
        )

        res = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "tts-1",
                "input": clean_snippet,
                "voice": req.voice or "alloy",
            },
            timeout=10,
        )

        if res.status_code == 200:
            return StreamingResponse(io.BytesIO(res.content), media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=res.status_code, detail=res.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "active_sessions": len(active_sessions),
        "telegram_alert_bot_set": bool(os.getenv("TELEGRAM_ALERT_BOT_TOKEN")),
        "telegram_alert_chat_set": bool(os.getenv("TELEGRAM_ALERT_CHAT_ID")),
        "telegram_bot_set": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "telegram_chat_set": bool(os.getenv("TELEGRAM_CHAT_ID")),
    }


# Mount static frontend export if built (for Hugging Face Spaces production deployment)
frontend_out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "out")
if os.path.exists(frontend_out):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_out, html=True), name="static_frontend")
