import os
import json
import requests
import queue
import threading
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

load_dotenv()

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


def queue_chat_history_to_telegram(
    session_id: str,
    user_input: str,
    assistant_response: str,
) -> str:
    _submit_background_task("chat_history_log", send_chat_history_to_telegram, session_id, user_input, assistant_response)
    return "QUEUED: chat history scheduled."


def send_chat_history_to_telegram(
    session_id: str,
    user_input: str,
    assistant_response: str,
) -> str:
    token, chat_id = _get_telegram_target(debug=False)
    if not token or not chat_id:
        return "FAILED: Telegram credentials missing."

    clean_user = _escape_html(_safe_truncate(user_input, 1500))
    clean_ai = _escape_html(_safe_truncate(assistant_response, 2500))

    html = (
        f"<b>💬 CHAT LOG</b>\n"
        f"<b>Session:</b> <code>{_escape_html(session_id)}</code>\n\n"
        f"<b>👤 User:</b>\n{clean_user}\n\n"
        f"<b>🤖 Arun's Assistant:</b>\n{clean_ai}"
    )

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="chat_log",
    )


def send_debug_event_to_telegram(
    event_type: str,
    payload_summary: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    if not _is_telegram_debug_enabled():
        return "SKIPPED: debug disabled."

    token, chat_id = _get_telegram_target(debug=True)
    if not token or not chat_id:
        return "FAILED: Telegram debug credentials missing."

    clean_event = _escape_html(event_type.upper())
    clean_payload = _escape_html(_safe_truncate(payload_summary, 2000))

    meta_str = ""
    if metadata:
        meta_str = "\n".join([f"• <b>{_escape_html(str(k))}:</b> {_escape_html(str(v))}" for k, v in metadata.items()])

    html = f"<b>🔧 DEBUG EVENT: {clean_event}</b>\n{meta_str}\n\n<code>{clean_payload}</code>"

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="debug_event",
    )


def _escape_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


ALLOWED_NOTIFY_CATEGORIES = {
    "UNKNOWN_QUESTION",
    "URGENT",
    "FEEDBACK",
    "SYSTEM_ALERT",
    "LEAD",
}

_RECENT_ALERTS: Dict[str, float] = {}
_ALERT_DEDUP_WINDOW_SECONDS = 120.0


def _should_send_alert(category: str, user_input: str) -> bool:
    import time
    now = time.time()

    expired_keys = [k for k, timestamp in _RECENT_ALERTS.items() if now - timestamp > _ALERT_DEDUP_WINDOW_SECONDS]
    for k in expired_keys:
        _RECENT_ALERTS.pop(k, None)

    key = f"{category.upper()}:{user_input.strip().lower()}"
    if key in _RECENT_ALERTS:
        return False

    _RECENT_ALERTS[key] = now
    return True


def _deliver_notify_arun(
    category: str,
    user_input: str,
    user_metadata_json: str = "",
    fast: bool = False,
) -> str:
    token, chat_id = _get_telegram_target(alert=True)

    if not token or not chat_id:
        return "FAILED: Telegram credentials missing."

    category = (category or "UNKNOWN_QUESTION").strip().upper()
    if category not in ALLOWED_NOTIFY_CATEGORIES:
        category = "UNKNOWN_QUESTION"

    cleaned_input = _safe_truncate(user_input, 1200)

    if not _should_send_alert(category, cleaned_input):
        return f"SKIPPED: duplicate {category} alert suppressed."

    html = (
        f"<b>🚨 URGENT LEAD / ALERT: {category}</b>\n\n"
        f"<b>User Query / Details:</b>\n{_escape_html(cleaned_input)}\n\n"
        f"<b>Direct Contact:</b>\n"
        f"• Phone: +91 8881109193\n"
        f"• Email: neural.arun.dev@gmail.com"
    )

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="notify_arun_bg",
    )


@tool
def notify_arun(category: str, user_input: str, user_metadata_json: str = "") -> str:
    """Send an instant Telegram alert to Arun's phone for urgent contact requests, leads, or unknown questions."""
    _submit_background_task(
        "notify_arun_bg",
        _deliver_notify_arun,
        category,
        user_input,
        user_metadata_json,
    )
    return f"Telegram alert queued to Arun's phone under category: {category.upper()}"


@tool
def search_arun_knowledge(query: str) -> str:
    """Search Arun's local knowledge base (ChromaDB + BM25 + Cohere Reranker) for information about his projects, architecture, philosophy, and background."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "data", "github")

    results = []
    if os.path.exists(docs_dir):
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(q.lower() in content.lower() for q in query.split()):
                            results.append(f"--- File: {file} ---\n{content[:1500]}")

    if results:
        return "\n\n".join(results[:3])
    return "No exact match found in knowledge base. Recommend asking Arun directly."


@tool
def get_github_live_data(username: str = "neural-arun") -> str:
    """Fetch live GitHub repository data and recent commits for Arun Yadav."""
    try:
        res = requests.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10", timeout=5)
        if res.status_code == 200:
            repos = res.json()
            lines = [f"• [{r['name']}]({r['html_url']}) - {r.get('description', 'No description')} (Updated: {r['updated_at'][:10]})" for r in repos]
            return "### Live GitHub Repositories:\n" + "\n".join(lines)
    except Exception as e:
        return f"GitHub fetch error: {e}"
    return "Could not fetch GitHub data."


def run_pre_escalation(user_input: str, tool_map: dict) -> dict:
    lowered = (user_input or "").lower()
    urgent_keywords = ["hire", "contact", "talk to arun", "call arun", "meet arun", "whatsapp", "urgent", "consult", "project inquiry", "work together"]

    for kw in urgent_keywords:
        if kw in lowered:
            return {"escalate": True, "reason": f"Urgent contact keyword detected: '{kw}'"}

    return {"escalate": False, "reason": ""}


def queue_maybe_notify_arun(user_input: str, reason: str, channel: str = "api", session_id: str = ""):
    _submit_background_task(
        "maybe_notify_arun",
        _deliver_notify_arun,
        "URGENT",
        f"Reason: {reason}\nQuery: {user_input}",
    )


class RollingMemory:
    def __init__(self, summary_llm, max_turns: int = 4):
        self.summary_llm = summary_llm
        self.max_turns = max_turns
        self.history: List[Any] = []
        self.running_summary: str = "No prior summary. This is the start of the conversation."
        self.invocation_count = 0

    def add_interaction(self, human_text: str, ai_text: str):
        self.history.append(HumanMessage(content=human_text))
        self.history.append(AIMessage(content=ai_text))
        self.invocation_count += 1

        if self.invocation_count >= self.max_turns:
            self._summarize_and_prune()

    def _summarize_and_prune(self):
        print("\n[SYSTEM] Triggering background summarization...")
        messages_to_summarize = self.history[:-4]

        if not messages_to_summarize:
            return

        chat_transcript = "\n".join(
            [f"{'User' if isinstance(m, HumanMessage) else 'Arun Assistant'}: {m.content}" for m in messages_to_summarize]
        )

        prompt = (
            "You are an internal memory compression engine for Arun's AI Assistant.\n"
            "Merge the existing summary with the new transcript. Preserve technical context, names, project mentions, user goals, and important decisions. "
            "Keep it concise and stable. Return no more than 5 sentences.\n\n"
            f"--- EXISTING SUMMARY ---\n{self.running_summary}\n\n"
            f"--- NEW CHAT TO MERGE ---\n{chat_transcript}"
        )

        try:
            res = self.summary_llm.invoke([SystemMessage(content=prompt)])
            self.running_summary = res.content.strip()
            self.history = self.history[-4:]
            self.invocation_count = len(self.history) // 2
            print(f"[SYSTEM] Memory compressed. New summary: {self.running_summary[:120]}...")
        except Exception as e:
            print(f"[SYSTEM ERROR] Failed to summarize memory: {e}")

    def get_messages(self):
        return self.history


def init_agent():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set in environment.")

    summary_llm = ChatOpenAI(
        temperature=0.0,
        model="gpt-4o-mini",
        api_key=openai_key,
    )

    tools = [notify_arun, search_arun_knowledge, get_github_live_data]

    main_llm = ChatOpenAI(
        temperature=0.4, # Witty, casual, sharp tone
        model="gpt-4o-mini",
        api_key=openai_key,
    ).bind_tools(tools)

    profile, rules = load_static_context()

    system_prompt = f"""
You are **Arun's AI Assistant** — the personal AI assistant for Arun Yadav (AI Systems Architect specializing in Healthcare & Education).

BEHAVIOR & STYLE (EXACT INSTRUCTIONS):
Respond in a very casual, fun, and friendly style, just like a chill Indian boy naturally. Be straightforward, witty, savage when needed, but always helpful and truthful.

KEY RULES:
- Never sound like a typical boring AI. Talk like a cool friend.
- Keep replies natural, short when possible, but detailed when needed.
- Add emojis naturally 😄🔥🚀
- Be maximally truthful, no corporate bakchodi.
- If user talks in Hindi, reply mostly in same vibe.
- Crack jokes, roast lightly if situation demands.
- Never lecture morally unless seriously asked.

HIRING & CONTACT WORKFLOW:
- If someone asks "how to hire Arun", "want to talk to Arun", "contact details", or discusses a project/collaboration/hiring opportunity:
  1. Immediately provide Arun's direct contact details:
     • 📞 **Phone / Call:** +91 8881109193
     • 💬 **WhatsApp:** [+91 8881109193](https://wa.me/918881109193)
     • ✉️ **Email:** neural.arun.dev@gmail.com
  2. Ask for their Name, Email/Phone, and a quick summary of what they want to build so you can ping Arun directly on his phone!
  3. Call `notify_arun` (category `LEAD` or `URGENT`) to transmit an instant Telegram alert to Arun's phone!

CRITICAL TOOL RULES:
- For questions about Arun's background, architecture, projects, RAG engines, or code repos, call `search_arun_knowledge` or `get_github_live_data`. ALWAYS include clickable GitHub links!
- If search results are empty or the question is unknown, call `notify_arun` (category `UNKNOWN_QUESTION`) and tell the user you're pinging Arun to check!

--- IDENTITY PROFILE ---
{profile}

--- RULES OF ENGAGEMENT ---
{rules}

--- PAST CONVERSATION SUMMARY ---
{{running_summary}}
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    memory = RollingMemory(summary_llm=summary_llm)

    return main_llm, prompt, memory, tools


def queue_debug_event(
    event_type: str,
    payload_summary: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    _submit_background_task(
        "debug_event",
        send_debug_event_to_telegram,
        event_type,
        payload_summary,
        metadata,
    )
