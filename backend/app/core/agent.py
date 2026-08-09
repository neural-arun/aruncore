"""Agent composition root + backwards-compatible facade.

The heavy lifting previously in this file now lives in single-responsibility
services (notification, knowledge, memory, prompt, tools, tenant). This module
only: (1) applies the global IPv4-only DNS patch once, (2) exposes `init_agent`
as the small factory that wires an LLM + bound tools + chat prompt + memory,
and (3) re-exports every public symbol the API, Telegram bot, eval scripts,
and tests still import from `backend.app.core.agent`.
"""
import os
import socket
from typing import Any, Dict, Optional, Tuple

# Force IPv4-only DNS resolution (Hugging Face Spaces / dual-stack hosts can
# stall IPv6 lookups). Applied once at import time, mirroring the legacy boot.
try:
    _orig_getaddrinfo = socket.getaddrinfo

    def _ipv4_only_getaddrinfo(*args, **kwargs):
        res = _orig_getaddrinfo(*args, **kwargs)
        ipv4_res = [r for r in res if r[0] == socket.AF_INET]
        return ipv4_res or res

    socket.getaddrinfo = _ipv4_only_getaddrinfo
except Exception:
    pass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from backend.app.services.memory_manager import RollingMemory, MemoryManager
from backend.app.services.prompt_builder import PromptBuilder
from backend.app.services.tool_executor import (
    ToolExecutor,
    search_arun_knowledge,
    get_github_live_data,
    notify_arun,
)
from backend.app.services.tenant_service import tenant_service, TenantService
from backend.app.services.knowledge_service import knowledge_service
from backend.app.services.notification_service import (
    queue_debug_event,
    queue_maybe_notify_arun,
    queue_chat_history_to_telegram,
    queue_automated_chat_alert,
    send_automated_chat_alert,
    send_chat_history_to_telegram,
    send_debug_event_to_telegram,
    schedule_notify_arun,
    TELEGRAM_DELIVERY_LOGS,
    _deliver_notify_arun,
)
from backend.app.services.auth_service import generate_admin_token, verify_admin_token
from backend.app.services.agent_runner import AgentRunner, agent_runner, run_pre_escalation

load_dotenv()

__all__ = [
    "init_agent",
    "RollingMemory",
    "MemoryManager",
    "load_static_context",
    "load_tutor_config",
    "save_unknown_question_answer",
    "queue_debug_event",
    "queue_maybe_notify_arun",
    "run_pre_escalation",
    "queue_chat_history_to_telegram",
    "queue_automated_chat_alert",
    "send_automated_chat_alert",
    "send_chat_history_to_telegram",
    "send_debug_event_to_telegram",
    "schedule_notify_arun",
    "generate_admin_token",
    "verify_admin_token",
    "TELEGRAM_DELIVERY_LOGS",
    "search_arun_knowledge",
    "get_github_live_data",
    "notify_arun",
    "ToolExecutor",
    "AgentRunner",
    "agent_runner",
]


def init_agent(
    temperature: float = 0.4,
    model_name: Optional[str] = None,
    tutor_id: Optional[str] = None,
):
    """Build a ready-to-run ArunCore agent.

    Returns the same 4-tuple as the legacy factory:
    (main_llm, chat_prompt, memory, tools).
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set in environment.")

    resolved_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

    tools = ToolExecutor.get_enabled_tools(ToolExecutor.DEFAULT_TOOLS)
    main_llm = ChatOpenAI(
        temperature=temperature,
        model=resolved_model,
        api_key=openai_key,
    ).bind_tools(tools)

    system_prompt = PromptBuilder().build_system_prompt(tutor_id=tutor_id)
    prompt = PromptBuilder.build_chat_prompt(system_prompt)

    summary_llm = ChatOpenAI(
        temperature=0.0,
        model="gpt-4o-mini",
        api_key=openai_key,
    )
    memory = RollingMemory(summary_llm=summary_llm)

    return main_llm, prompt, memory, tools


def load_tutor_config(tutor_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Legacy demos-dictionary loader (kept for external consumers)."""
    return tenant_service.load_legacy_tutor_config(tutor_id)


def save_unknown_question_answer(question: str, answer: str) -> str:
    """Persists a verified Q&A pair into the active-learning store."""
    return knowledge_service.save_verified_answer(question, answer)


def load_static_context():
    """Canonical 5-tuple static context reader (system, guardrails, handoff, profile, rules)."""
    from backend.app.services.prompt_builder import load_static_context as _load_5

    return _load_5()