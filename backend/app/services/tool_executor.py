from typing import Dict, Any, List, Optional
from langchain_core.tools import tool


@tool
def search_courses(query: str) -> str:
    """Search tenant course catalog and track curriculum."""
    return f"Retrieved course details for query: '{query}'."


@tool
def book_calendar(date: str, topic: str) -> str:
    """Book a consultation session or mentorship call."""
    return f"Consultation session requested for '{topic}' on {date}."


@tool
def faq_lookup(question: str) -> str:
    """Search tenant FAQ knowledge base."""
    return f"Retrieved verified FAQ answers for: '{question}'."


class ToolExecutor:
    AVAILABLE_TOOLS = {
        "search_courses": search_courses,
        "book_calendar": book_calendar,
        "faq_lookup": faq_lookup,
    }

    @classmethod
    def get_enabled_tools(cls, enabled_tool_names: List[str]) -> List[Any]:
        tools: List[Any] = []
        for name in enabled_tool_names:
            if name in cls.AVAILABLE_TOOLS:
                tools.append(cls.AVAILABLE_TOOLS[name])
        return tools

    @classmethod
    def get_tool_map(cls, enabled_tool_names: List[str]) -> Dict[str, Any]:
        return {t.name: t for t in cls.get_enabled_tools(enabled_tool_names)}
