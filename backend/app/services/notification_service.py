"""Telegram notification & alert delivery.

All outgoing Telegram traffic is consolidated here: chat history logging,
debug events, per-message live chat alerts with the 1-Click Join link, and
the category-based notify_arun escalation system. Every call is fire-and-forget
via the shared background queue so the chat loop never blocks on the network.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple

from backend.app.services.background import submit_background_task
from backend.app.services.auth_service import generate_admin_token


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


def safe_truncate(text: str, limit: int = 1500) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."


def _escape_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


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


TELEGRAM_DELIVERY_LOGS: List[Dict[str, Any]] = []


def _record_telegram_log(label: str, status: str, detail: str) -> None:
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "label": label,
        "status": status,
        "detail": detail,
    }
    TELEGRAM_DELIVERY_LOGS.append(entry)
    if len(TELEGRAM_DELIVERY_LOGS) > 30:
        TELEGRAM_DELIVERY_LOGS.pop(0)


def _send_telegram_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    max_attempts: int = 3,
    delivery_label: str = "default",
    retry_sleep_seconds: float = 1.0,
) -> str:
    import urllib.request
    import urllib.parse
    import ssl

    token = (token or "").strip()
    if token.lower().startswith("bot"):
        token = token[3:].strip()

    chat_id = (chat_id or "").strip()

    if not token or not chat_id:
        msg = f"FAILED: Token or Chat ID empty (token_len={len(token)}, chat_id_len={len(chat_id)})"
        _record_telegram_log(delivery_label, "MISSING_CREDS", msg)
        print(f"[TELEGRAM:{delivery_label}] {msg}")
        return msg

    chunks = _chunk_text(text)
    total_chunks = len(chunks)

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    for idx, chunk in enumerate(chunks, 1):
        payload: Dict[str, Any] = {
            "token": token,
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        sent_chunk = False
        last_error = ""

        # Attempt 1: Try Vercel Serverless Relay (bypasses HF Space Telegram firewall block)
        relay_url = "https://aruncore.vercel.app/api/telegram"
        try:
            relay_data = json.dumps(payload).encode("utf-8")
            relay_req = urllib.request.Request(
                relay_url,
                data=relay_data,
                headers={"Content-Type": "application/json", "User-Agent": "ArunCore/1.0", "Connection": "close"},
            )
            with urllib.request.urlopen(relay_req, timeout=8, context=ssl_ctx) as resp:
                resp_bytes = resp.read()
                resp_data = json.loads(resp_bytes.decode("utf-8"))
                if resp.status == 200 and resp_data.get("ok"):
                    sent_chunk = True
        except Exception as e:
            last_error = f"Vercel Relay error: {e}"

        if not sent_chunk:
            # Direct Telegram API Fallback
            for attempt in range(1, max_attempts + 1):
                try:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    direct_payload = {
                        "chat_id": chat_id,
                        "text": chunk,
                        "disable_web_page_preview": True,
                    }
                    if parse_mode:
                        direct_payload["parse_mode"] = parse_mode

                    data = json.dumps(direct_payload).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=data,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "ArunCore/1.0",
                            "Connection": "close",
                        },
                    )
                    with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
                        resp_bytes = resp.read()
                        resp_data = json.loads(resp_bytes.decode("utf-8"))
                        if resp.status == 200 and resp_data.get("ok"):
                            sent_chunk = True
                            break
                        else:
                            last_error = f"HTTP {resp.status}: {resp_bytes.decode('utf-8')[:200]}"
                except Exception as e:
                    last_error = str(e)

                if attempt < max_attempts:
                    time.sleep(retry_sleep_seconds)

        if not sent_chunk and parse_mode == "HTML":
            fallback_payload = {
                "chat_id": chat_id,
                "text": f"[{delivery_label}] (Plain Text Fallback {idx}/{total_chunks})\n{chunk}",
                "disable_web_page_preview": True,
            }
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = json.dumps(fallback_payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "ArunCore/1.0",
                        "Connection": "close",
                    },
                )
                with urllib.request.urlopen(req, timeout=12, context=ssl_ctx) as resp:
                    resp_bytes = resp.read()
                    resp_data = json.loads(resp_bytes.decode("utf-8"))
                    if resp.status == 200 and resp_data.get("ok"):
                        sent_chunk = True
            except Exception as e:
                last_error = f"Fallback error: {e}"

        if not sent_chunk:
            err_msg = f"FAILED chunk {idx}/{total_chunks}: {last_error}"
            print(f"[TELEGRAM:{delivery_label}] {err_msg}")
            _record_telegram_log(delivery_label, "ERROR", err_msg)
            return err_msg

    print(f"[TELEGRAM:{delivery_label}] SUCCESS")
    _record_telegram_log(delivery_label, "SUCCESS", f"Delivered {total_chunks} chunk(s)")
    return "SUCCESS: message delivered."


def send_chat_history_to_telegram(
    session_id: str,
    user_input: str,
    assistant_response: str,
    thoughts: Optional[List[str]] = None,
    tool_calls: Optional[List[str]] = None,
    retrieved_chunks: Optional[List[str]] = None,
    github_data: Optional[List[str]] = None,
) -> str:
    token, chat_id = _get_telegram_target(debug=False)
    if not token or not chat_id:
        return "FAILED: Telegram credentials missing."

    clean_user = _escape_html(safe_truncate(user_input, 1500))
    clean_ai = _escape_html(safe_truncate(assistant_response, 2500))

    tools_html = ""
    if tool_calls and len(tool_calls) > 0:
        tools_str = "\n".join([f"• <code>{_escape_html(safe_truncate(t, 250))}</code>" for t in tool_calls])
        tools_html = f"\n\n<b>🧠 AI Decisions & Tool Calls:</b>\n{tools_str}"

    chunks_html = ""
    if retrieved_chunks and len(retrieved_chunks) > 0:
        chunks_str = "\n".join([f"--- Chunk {i+1} ---\n{_escape_html(safe_truncate(c, 500))}" for i, c in enumerate(retrieved_chunks[:3])])
        chunks_html = f"\n\n<b>📚 RAG Knowledge Chunks Retrieved:</b>\n<code>{chunks_str}</code>"

    github_html = ""
    if github_data and len(github_data) > 0:
        github_str = "\n".join([f"--- Repo Data ---\n{_escape_html(safe_truncate(g, 500))}" for g in github_data[:2]])
        github_html = f"\n\n<b>🐙 Live GitHub Repositories Fetched:</b>\n<code>{github_str}</code>"

    thoughts_html = ""
    if thoughts and len(thoughts) > 0:
        thoughts_str = "\n".join([f"• {_escape_html(t)}" for t in thoughts])
        thoughts_html = f"\n\n<b>⚙️ Execution Steps:</b>\n{thoughts_str}"

    html = (
        f"<b>📊 ARUNCORE FULL EXECUTION TRACE</b>\n"
        f"<b>Session ID:</b> <code>{_escape_html(session_id)}</code>\n\n"
        f"<b>👤 User Question:</b>\n{clean_user}"
        f"{tools_html}"
        f"{chunks_html}"
        f"{github_html}"
        f"{thoughts_html}\n\n"
        f"<b>🤖 AI Twin Final Reply:</b>\n{clean_ai}"
    )

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="chat_log",
    )


def queue_chat_history_to_telegram(
    session_id: str,
    user_input: str,
    assistant_response: str,
    thoughts: Optional[List[str]] = None,
    tool_calls: Optional[List[str]] = None,
    retrieved_chunks: Optional[List[str]] = None,
    github_data: Optional[List[str]] = None,
) -> str:
    submit_background_task(
        "chat_history_log",
        send_chat_history_to_telegram,
        session_id,
        user_input,
        assistant_response,
        thoughts or [],
        tool_calls or [],
        retrieved_chunks or [],
        github_data or [],
    )
    return "QUEUED: chat history scheduled."


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
    clean_payload = _escape_html(safe_truncate(payload_summary, 2000))

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


def queue_debug_event(
    event_type: str,
    payload_summary: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    submit_background_task(
        "debug_event",
        send_debug_event_to_telegram,
        event_type,
        payload_summary,
        metadata,
    )


def send_automated_chat_alert(
    session_id: str,
    user_input: str,
    assistant_response: str,
) -> str:
    token, chat_id = _get_telegram_target(alert=True)
    if not token or not chat_id:
        return "FAILED: Telegram credentials missing."

    admin_tok = generate_admin_token(session_id)
    join_link = f"https://aruncore.vercel.app/?session_id={session_id}&admin_token={admin_tok}"

    clean_user = _escape_html(safe_truncate(user_input, 1000))
    clean_ai = _escape_html(safe_truncate(assistant_response, 1500))

    html = (
        f"🚨 <b>LIVE WEBSITE CHAT ACTIVITY</b>\n"
        f"<b>Session ID:</b> <code>{_escape_html(session_id)}</code>\n\n"
        f"<b>👤 User Question:</b>\n{clean_user}\n\n"
        f"<b>🤖 AI Response:</b>\n{clean_ai}\n\n"
        f"🔗 <b><a href=\"{join_link}\">👉 CLICK HERE TO JOIN LIVE CHAT AS REAL ARUN</a></b>"
    )

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="every_chat_alert",
    )


def queue_automated_chat_alert(session_id: str, user_input: str, assistant_response: str) -> None:
    submit_background_task(
        "automated_chat_alert_bg",
        send_automated_chat_alert,
        session_id,
        user_input,
        assistant_response,
    )


def queue_maybe_notify_arun(
    user_input: str,
    reason: str = "",
    channel: str = "api",
    session_id: str = "",
    final_response: str = "",
    scratchpad: Optional[list] = None,
    tool_map: Optional[dict] = None,
    user_metadata: Optional[dict] = None,
    pre_notified: bool = False,
) -> None:
    """Escalation hook: schedules an URGENT notify when contact intent is detected."""
    submit_background_task(
        "maybe_notify_arun",
        _deliver_notify_arun,
        "URGENT",
        f"Reason: {reason or 'General check'}\nQuery: {user_input}",
    )


_RECENT_ALERTS: Dict[str, float] = {}
_ALERT_DEDUP_WINDOW_SECONDS = 10.0


def _should_send_alert(category: str, user_input: str) -> bool:
    now = time.time()

    expired_keys = [k for k, timestamp in _RECENT_ALERTS.items() if now - timestamp > _ALERT_DEDUP_WINDOW_SECONDS]
    for k in expired_keys:
        _RECENT_ALERTS.pop(k, None)

    key = f"{category.upper()}:{user_input.strip().lower()}"
    if key in _RECENT_ALERTS:
        return False

    _RECENT_ALERTS[key] = now
    return True


ALLOWED_NOTIFY_CATEGORIES = {
    "UNKNOWN_QUESTION",
    "URGENT",
    "FEEDBACK",
    "SYSTEM_ALERT",
    "LEAD",
    "ABUSE",
    "WEIRD",
    "SUSPICIOUS",
    "OFF_TOPIC",
}

_CATEGORY_HEADERS = {
    "UNKNOWN_QUESTION": "🤷 UNKNOWN QUESTION",
    "LEAD":             "💼 NEW LEAD / HIRING INQUIRY",
    "URGENT":           "🚨 URGENT ALERT",
    "ABUSE":            "🤬 ABUSE / RUDE MESSAGE",
    "WEIRD":            "👀 WEIRD / UNUSUAL MESSAGE",
    "SUSPICIOUS":       "🕵️ SUSPICIOUS ACTIVITY",
    "OFF_TOPIC":        "🚫 OFF-TOPIC / IRRELEVANT",
    "FEEDBACK":         "💬 FEEDBACK",
    "SYSTEM_ALERT":     "⚙️ SYSTEM ALERT",
}


def _deliver_notify_arun(
    category: str,
    user_input: str,
    user_metadata_json: str = "",
    _fast: bool = False,
) -> str:
    token, chat_id = _get_telegram_target(alert=True)

    if not token or not chat_id:
        msg = "FAILED: Telegram credentials missing."
        _record_telegram_log("notify_arun_bg", "MISSING_CREDS", msg)
        return msg

    category = (category or "UNKNOWN_QUESTION").strip().upper()
    if category not in ALLOWED_NOTIFY_CATEGORIES:
        category = "UNKNOWN_QUESTION"

    cleaned_input = safe_truncate(user_input, 1200)

    if not _should_send_alert(category, cleaned_input):
        msg = f"SKIPPED: duplicate {category} alert suppressed within 10s window."
        _record_telegram_log("notify_arun_bg", "SKIPPED_DEDUP", msg)
        return msg

    header = _CATEGORY_HEADERS.get(category, f"🚨 ALERT: {category}")
    html = (
        f"<b>{header}</b>\n\n"
        f"<b>User Query / Details:</b>\n{_escape_html(cleaned_input)}\n\n"
        f"<b>Category:</b> {category}\n"
        f"<b>Contact:</b> +91 8881109193 | neural.arun.dev@gmail.com\n\n"
        f"<i>💡 Reply directly to this message to save your answer into AI memory!</i>"
    )

    return _send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=html,
        parse_mode="HTML",
        delivery_label="notify_arun_bg",
    )


def schedule_notify_arun(category: str, user_input: str, user_metadata_json: str = "") -> str:
    """Queue an urgent notify_arun Telegram alert (used by the agent tool)."""
    submit_background_task(
        "notify_arun_bg",
        _deliver_notify_arun,
        category,
        user_input,
        user_metadata_json or "",
    )
    return "QUEUED: notify_arun alert scheduled."