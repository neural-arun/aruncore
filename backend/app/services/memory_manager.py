"""Rolling conversation memory with summary-compression.

A single session's chat lives in a shrinking window. Every N turns the oldest
messages are folded into a compact running summary by the summary LLM, so long
conversations keep full context without blowing the token budget.
"""
from typing import Any, List, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class RollingMemory:
    """Stateful per-session memory used across API and Telegram chat loops."""

    def __init__(self, summary_llm: Any, max_turns: int = 4):
        self.summary_llm = summary_llm
        self.max_turns = max_turns
        self.history: List[BaseMessage] = []
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

    def get_messages(self) -> List[BaseMessage]:
        return self.history

    def clear(self):
        self.history.clear()
        self.running_summary = "No prior summary. This is the start of the conversation."
        self.invocation_count = 0


# Backwards-compatible alias: the decoupled API exposes this class as
# `MemoryManager` while the agent layer keeps the historical `RollingMemory` name.
MemoryManager = RollingMemory