"""Thread-safe in-memory session state for the ArunCore backend.

Consolidates all live websocket-like stores that were previously scattered
through the API module:

* message history per session (visitor + twin + real-human entries)
* human-owned messages
* human-control flags (3-way live chat takeover)
* rolling memory objects per session

All reads/writes are guarded by a global lock so concurrent chat streams
cannot corrupt shared dicts.
"""
import os
import time
import datetime
import threading
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI

from backend.app.services.memory_manager import RollingMemory


def _default_summary_llm():
    return ChatOpenAI(
        temperature=0.0,
        model=os.getenv("MEMORY_SUMMARY_MODEL", "gpt-4.1-nano"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )


class SessionStore:
    """Single ownership point for every in-memory session artifact."""

    def __init__(self, summary_llm_factory: Any = None):
        self._lock = threading.RLock()
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._human_messages: Dict[str, List[Dict[str, Any]]] = {}
        self._human_control: Dict[str, bool] = {}
        self._memories: Dict[str, RollingMemory] = {}
        self._summary_llm_factory = summary_llm_factory or _default_summary_llm

    @property
    def liveness(self) -> int:
        return len(self._memories)

    # ------------------------------------------------------------------ #
    # Message history
    # ------------------------------------------------------------------ #
    def record_message(self, session_id, sender, text, name="", thoughts=None):
        with self._lock:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            entry = {
                "id": f"msg_{sender}_{int(time.time() * 1000)}_{len(self._history.get(session_id, []))}",
                "sender": sender,
                "name": name or (
                    "Arun Yadav" if sender == "human_arun"
                    else "Arun's AI Assistant" if sender == "twin"
                    else "You"
                ),
                "text": text,
                "timestamp": now_str,
            }
            if thoughts:
                entry["thoughts"] = thoughts

            if session_id not in self._history:
                self._history[session_id] = []
            self._history[session_id].append(entry)
            return entry

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._history.get(session_id, []))

    def get_human_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._human_messages.get(session_id, []))

    def append_human_message(self, session_id: str, entry: Dict[str, Any]) -> None:
        with self._lock:
            self._human_messages.setdefault(session_id, []).append(entry)

    def get_human_entries(self, session_id: str) -> List[Dict[str, Any]]:
        """Channel messages authored by the real human within this session."""
        with self._lock:
            return [m for m in self._history.get(session_id, []) if m.get("sender") == "human_arun"]

    def get_last_user_message(self, session_id: str) -> str:
        with self._lock:
            for m in reversed(self._history.get(session_id, [])):
                if m.get("sender") == "user":
                    return m.get("text", "")
        return ""

    # ------------------------------------------------------------------ #
    # Human-control (3-way live takeover)
    # ------------------------------------------------------------------ #
    def is_human_control(self, session_id: str) -> bool:
        with self._lock:
            return bool(self._human_control.get(session_id, False))

    def set_human_control(self, session_id: str, enabled: bool) -> None:
        with self._lock:
            self._human_control[session_id] = enabled

    # ------------------------------------------------------------------ #
    # Rolling memory per session
    # ------------------------------------------------------------------ #
    def get_or_create_memory(self, session_id: str) -> RollingMemory:
        with self._lock:
            if session_id not in self._memories:
                self._memories[session_id] = RollingMemory(
                    summary_llm=self._summary_llm_factory(),
                )
            return self._memories[session_id]


# Backwards-compatible global store (used by the FastAPI layer).
session_store = SessionStore()