from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class MemoryManager:
    def __init__(self, window_size: int = 10, summary_llm: Optional[Any] = None):
        self.window_size = window_size
        self.summary_llm = summary_llm
        self.history: List[BaseMessage] = []
        self.running_summary: str = "No prior summary. Starting fresh conversation."

    def add_interaction(self, user_msg: str, ai_msg: str):
        self.history.append(HumanMessage(content=user_msg))
        self.history.append(AIMessage(content=ai_msg))

        if len(self.history) > self.window_size * 2:
            overflow_count = len(self.history) - (self.window_size * 2)
            overflow_msgs = self.history[:overflow_count]
            self.history = self.history[overflow_count:]

            if self.summary_llm:
                try:
                    summary_prompt = f"Existing Summary:\n{self.running_summary}\n\nNew Old Interactions to Summarize:\n"
                    for m in overflow_msgs:
                        prefix = "User" if isinstance(m, HumanMessage) else "Assistant"
                        summary_prompt += f"{prefix}: {m.content}\n"
                    
                    res = self.summary_llm.invoke(summary_prompt)
                    if hasattr(res, "content") and res.content:
                        self.running_summary = str(res.content).strip()
                except Exception as e:
                    print(f"[MEMORY_MANAGER WARNING] Summary generation failed: {e}")

    def get_messages(self) -> List[BaseMessage]:
        return self.history

    def clear(self):
        self.history.clear()
        self.running_summary = "No prior summary. Starting fresh conversation."
