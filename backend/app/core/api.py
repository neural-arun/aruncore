"""ArunCore FastAPI HTTP layer.

This file only wires HTTP: request validation, routing, CORS, and static file
serving. Every piece of business logic lives in single-responsibility services
and is delegated here (agent runner loops, session store, notification, voice,
tenant config, auth, knowledge persistence).
"""
import os
import json
import io
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.app.core.agent import init_agent, verify_admin_token
from backend.app.services.session_store import session_store
from backend.app.services.agent_runner import agent_runner
from backend.app.services.knowledge_service import knowledge_service
from backend.app.services.tenant_service import tenant_service
from backend.app.services.notification_service import TELEGRAM_DELIVERY_LOGS

load_dotenv()

app = FastAPI(title="ArunCore API", description="Stateful Agentic Backend for Arun Yadav's Digital Twin.")

# Enable CORS for external frontends (Vercel, custom domains, local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the ArunCore engine once (mirrors legacy boot).
try:
    print("Initializing ArunCore API Backend...")
    _, _, _, tools = init_agent()
    global_tool_map = {t.name: t for t in tools}
    print("API Backend Initialized Successfully.")
except Exception as e:
    print(f"Failed to initialize backend: {e}")
    raise e


class ChatRequest(BaseModel):
    session_id: str
    message: str
    tutor_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"


class HumanMessageRequest(BaseModel):
    session_id: str
    admin_token: str
    message: str


@app.get("/api/config")
@app.get("/config")
async def get_tutor_config_endpoint(tutor: Optional[str] = None):
    cfg = tenant_service.load_legacy_tutor_config(tutor)
    if not cfg:
        return {"tutor_id": tutor or "arun", "config": None}
    cfg["tutor_id"] = tutor or "arun"
    return cfg


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    async def generate_response():
        async for chunk in agent_runner.stream_chat(
            session_id=req.session_id,
            message=req.message,
            tutor_id=req.tutor_id,
            tool_map=global_tool_map,
        ):
            yield json.dumps(chunk) + "\n"

    return StreamingResponse(generate_response(), media_type="application/x-ndjson")


@app.post("/tts")
async def tts_endpoint(req: TTSRequest):
    from backend.app.services.voice_service import VoiceService

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        audio_bytes = VoiceService.generate_tts_audio(req.text, voice=req.voice or "alloy")
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    alert_tok = os.getenv("TELEGRAM_ALERT_BOT_TOKEN", "")
    bot_tok = os.getenv("TELEGRAM_BOT_TOKEN", "")
    alert_cid = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
    bot_cid = os.getenv("TELEGRAM_CHAT_ID")

    return {
        "status": "ok",
        "active_sessions": session_store.liveness,
        "telegram_alert_bot_preview": f"{alert_tok[:6]}...{alert_tok[-4:]}" if alert_tok else "MISSING",
        "telegram_alert_chat_id": alert_cid or "MISSING",
        "telegram_bot_preview": f"{bot_tok[:6]}...{bot_tok[-4:]}" if bot_tok else "MISSING",
        "telegram_chat_id": bot_cid or "MISSING",
        "telegram_logs": TELEGRAM_DELIVERY_LOGS[-10:],
    }


@app.post("/chat/human-message")
async def post_human_message(req: HumanMessageRequest):
    if not verify_admin_token(req.session_id, req.admin_token):
        raise HTTPException(status_code=403, detail="Invalid admin token.")

    clean_text = (req.message or "").strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    lowered = clean_text.lower().strip()

    # Command: /release or /resume -> Hand control back to AI Twin
    if lowered in ("/release", "/resume"):
        session_store.set_human_control(req.session_id, False)
        rel_entry = session_store.record_message(
            req.session_id, "human_arun",
            "[Handed back auto-response control to AI Twin]",
            name="Arun Yadav",
        )
        return {"status": "success", "entry": rel_entry, "human_control": False}

    # Command: /answer -> Trigger AI Twin to answer reading the 3-way transcript
    if lowered.startswith("/answer"):
        session_store.set_human_control(req.session_id, True)
        extra_prompt = clean_text[7:].strip()
        cmd_entry = session_store.record_message(
            req.session_id, "human_arun", f"/answer {extra_prompt}".strip(), name="Arun Yadav"
        )
        ai_reply = await agent_runner.trigger_ai_answer(req.session_id, extra_prompt)
        return {"status": "success", "entry": cmd_entry, "ai_reply": ai_reply, "human_control": True}

    # Real Arun's first human message activates Human Control Mode
    session_store.set_human_control(req.session_id, True)
    entry = session_store.record_message(req.session_id, "human_arun", clean_text, name="Arun Yadav")
    session_store.append_human_message(req.session_id, entry)

    last_user_msg = session_store.get_last_user_message(req.session_id)

    if last_user_msg:
        try:
            knowledge_service.save_verified_answer(last_user_msg, clean_text)
            print(f"[RAG AUTO-UPDATE] Saved Q&A pair to unknown_questions.json & triggered ChromaDB re-ingestion.")
        except Exception as e:
            print(f"[RAG AUTO-UPDATE ERROR] Failed to auto-ingest admin answer: {e}")

    memory = session_store.get_or_create_memory(req.session_id)
    memory.add_interaction(f"[REAL ARUN JOINED LIVE]: {clean_text}", "Acknowledged real Arun input.")

    return {"status": "success", "entry": entry, "human_control": True}


@app.get("/chat/history")
async def get_chat_history(session_id: str):
    msgs = session_store.get_history(session_id)
    return {"session_id": session_id, "messages": msgs}


@app.get("/chat/human-messages")
async def get_human_messages(session_id: str):
    msgs = session_store.get_human_messages(session_id)
    return {"session_id": session_id, "messages": msgs}


@app.get("/chat/verify-admin-token")
async def verify_admin(session_id: str, admin_token: str):
    valid = verify_admin_token(session_id, admin_token)
    return {"valid": valid, "session_id": session_id}


# Mount static frontend export if built (for Hugging Face Spaces production deployment)
frontend_out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "out")
if os.path.exists(frontend_out):
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=frontend_out, html=True), name="static_frontend")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)