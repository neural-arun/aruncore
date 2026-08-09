"""Config-driven tool registry for the ArunCore agent.

Every tool the LLM may call is defined here and exposed through `ToolExecutor`.
A tenant's `enabled_tools` array (agent.json) simply selects which tools get
bound into the LLM execution loop — no Python edits required to add a client.
"""
from typing import Dict, Any, List, Optional

from langchain_core.tools import tool

from backend.app.services.knowledge_service import knowledge_service
from backend.app.services.notification_service import schedule_notify_arun


# ---------------------------------------------------------------------- #
# Legacy placeholder tools (kept for tenant agent.json enabled_tools and  #
# the demo dictionary path; not bound by the core Arun twin agent).       #
# ---------------------------------------------------------------------- #
@tool
def search_courses(query: str) -> str:
    """Search tenant course catalog and curriculum."""
    return f"Retrieved course details for query: '{query}'."


@tool
def book_calendar(date: str, topic: str) -> str:
    """Book a consultation session or mentorship call."""
    return f"Consultation session requested for '{topic}' on {date}."


@tool
def faq_lookup(question: str) -> str:
    """Search tenant FAQ knowledge base."""
    return f"Retrieved verified FAQ answers for: '{question}'."


# ---------------------------------------------------------------------- #
# ArunCore real agent tools                                              #
# ---------------------------------------------------------------------- #
@tool
def search_arun_knowledge(query: str) -> str:
    """Search Arun's local knowledge base for information about his projects, architecture, philosophy, and background."""
    return knowledge_service.search(query)


@tool
def get_github_live_data(username: str = "neural-arun") -> str:
    """Fetch live GitHub repository data and recent commits for Arun Yadav."""
    return knowledge_service.fetch_live_github(username)


@tool
def notify_arun(category: str, user_input: str, user_metadata_json: str = "") -> str:
    """Send an instant Telegram alert to Arun's phone ONLY when a visitor explicitly asks to hire, consult, or contact Arun (LEAD), asks an unknown technical question (UNKNOWN_QUESTION), or requests urgent assistance (URGENT). Do NOT call this tool for general questions or identity questions like 'who are you'."""
    schedule_notify_arun(category, user_input, user_metadata_json)
    return (
        f"Successfully sent Telegram alert to Arun's phone (Category: {category.upper()}).\n"
        "YOU MUST NOW OUTPUT ARUN'S DIRECT CONTACT DETAILS IN BULLET POINTS:\n"
        "- 📞 Phone: +91 8881109193\n"
        "- 💬 WhatsApp: https://wa.me/918881109193\n"
        "- ✉️ Email: neural.arun.dev@gmail.com\n"
        "- 💼 LinkedIn: https://www.linkedin.com/in/arun-yadav-768052368\n"
        "- 🌐 GitHub: https://github.com/neural-arun"
    )


class ToolExecutor:
    """Dynamic, config-driven tool registry bound into the LLM loop."""

    DEFAULT_TOOLS = ["search_arun_knowledge", "get_github_live_data", "notify_arun"]

    AVAILABLE_TOOLS = {
        "search_courses": search_courses,
        "book_calendar": book_calendar,
        "faq_lookup": faq_lookup,
        "search_arun_knowledge": search_arun_knowledge,
        "get_github_live_data": get_github_live_data,
        "notify_arun": notify_arun,
    }

    @classmethod
    def get_enabled_tools(cls, enabled_tool_names: Optional[List[str]]) -> List[Any]:
        names = enabled_tool_names or cls.DEFAULT_TOOLS
        tools: List[Any] = []
        for name in names:
            if name in cls.AVAILABLE_TOOLS:
                tools.append(cls.AVAILABLE_TOOLS[name])
        return tools

    @classmethod
    def get_tool_map(cls, enabled_tool_names: Optional[List[str]]) -> Dict[str, Any]:
        return {t.name: t for t in cls.get_enabled_tools(enabled_tool_names)}