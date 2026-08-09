"""System prompt assembly for the ArunCore agent.

Every tenant-facing prompt (both the legacy demos dictionary and the split
tenant configs) flows through here. The builder returns the exact same prompt
templates the legacy monolith produced, so prompt behavior is unchanged while
the assembly itself lives in a single-responsibility service.
"""
import os
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from backend.app.services.tenant_service import TenantService


def _backend_app_dir() -> str:
    """backend/app/ (parent of services/, core/, prompts/, ...)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project_root() -> str:
    """profile/ (repository root)."""
    return os.path.dirname(_backend_app_dir())


def load_static_context() -> Tuple[str, str, str, str, str]:
    """Returns (system_prompt, guardrails, handoff, profile, rules).

    The prompts/ directory may be absent on a fresh checkout; every missing
    file simply resolves to an empty string, matching the legacy loader.
    """
    backend_app = _backend_app_dir()
    root_dir = _project_root()

    sys_prompt_path = os.path.join(backend_app, "prompts", "system_prompt.md")
    guardrails_path = os.path.join(backend_app, "prompts", "guardrails.md")
    handoff_path = os.path.join(backend_app, "prompts", "handoff_prompt.md")

    profile_path = os.path.join(root_dir, "data", "static", "public_profile.md")
    rules_path = os.path.join(root_dir, "data", "static", "rules_of_engagement.md")

    def _read(path: str) -> str:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    return (
        _read(sys_prompt_path),
        _read(guardrails_path),
        _read(handoff_path),
        _read(profile_path),
        _read(rules_path),
    )


class PromptBuilder:
    """Constructs the final system prompt + chat template for an agent run."""

    def __init__(self, tenant_service_: Optional[TenantService] = None):
        self.tenant_service = tenant_service_ or TenantService()

    def build_system_prompt(self, tutor_id: Optional[str] = None) -> str:
        """Assembles the system prompt for either a tenant (demos dict) or the
        default Arun twin persona. Contains a literal ``{running_summary}``
        placeholder that the chat template fills per message."""
        tutor_cfg = self.tenant_service.load_legacy_tutor_config(tutor_id)

        if tutor_cfg:
            backend_cfg = tutor_cfg.get("backend_llm_configuration", {})
            sys_prompt_cfg = backend_cfg.get("system_prompt", {})

            custom_prompt = sys_prompt_cfg.get("persona_identity") or tutor_cfg.get("custom_system_prompt") or "You are an AI Course Advisor."
            rules_list = sys_prompt_cfg.get("project_guidelines") or tutor_cfg.get("custom_rules") or []
            courses_data = tutor_cfg.get("courses") or []
            about_bio = tutor_cfg.get("frontend_ui_dictionary", {}).get("about_view", {}).get("bio_paragraphs") or tutor_cfg.get("about_text") or ""

            rules_txt = "\n".join([f"- {r}" for r in rules_list])
            courses_txt = json_dumps_safe(courses_data)
            about_txt = "\n".join(about_bio) if isinstance(about_bio, list) else str(about_bio)

            return f"""
{custom_prompt}

--- INSTRUCTOR & COURSE KNOWLEDGE ---
About Instructor:
{about_txt}

Available Courses & Cohorts:
{courses_txt}

--- SPECIAL INSTRUCTIONS & RULES ---
{rules_txt}

--- LANGUAGE RULES ---
Always respond in the exact language used by the student (English or natural Hinglish).

--- PAST CONVERSATION SUMMARY ---
{{running_summary}}
"""

        sys_content, guard_content, handoff_content, profile, rules = load_static_context()

        return f"""
--- MASTER RULES OF ENGAGEMENT & PERSONA (PRIMARY CORE) ---
{rules}

--- IDENTITY PROFILE & TECHNICAL SPECIFICATIONS ---
{profile}

--- GUARDRAILS & STEERING RULES ---
{guard_content}

--- 3-WAY LIVE CHAT & HANDOFF RULES ---
{handoff_content}

--- PAST CONVERSATION SUMMARY ---
{{running_summary}}
"""

    @staticmethod
    def build_chat_prompt(system_prompt: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    @staticmethod
    def inject_live_human_notice(messages: List[Any], arun_human_msgs: List[Dict[str, Any]]) -> List[Any]:
        """Inserts the 3-way live chat presence notice when the real human is active."""
        if not arun_human_msgs:
            return messages

        formatted_msgs = "\n".join([f"• Real Human Instructor (👨‍💻): \"{m.get('text')}\"" for m in arun_human_msgs])
        live_notice = SystemMessage(content=(
            f"🟢 CRITICAL LIVE 3-WAY CHAT NOTICE (REAL HUMAN INSTRUCTOR IS PRESENT):\n"
            f"The REAL HUMAN INSTRUCTOR (👨‍💻) HAS JOINED THIS CHAT ROOM LIVE AND IS CURRENTLY CHATTING!\n\n"
            f"REAL INSTRUCTOR'S MESSAGES IN THIS SESSION:\n{formatted_msgs}\n\n"
            f"MANDATORY INSTRUCTIONS FOR AI ASSISTANT IN THIS 3-WAY CHAT:\n"
            f"1. Acknowledge that the REAL human instructor is present right next to you in this chat session!\n"
            f"2. If the user asks how the instructor came here or questions about their arrival, explain enthusiastically: \"The real instructor tapped their 1-Click Telegram link and joined our chat live from their phone! So both of us (Real Instructor + AI Assistant) are here together with you!\"\n"
            f"3. Never confuse yourself as the human — you are the AI Assistant co-piloting alongside the Real Instructor!"
        ))

        new_messages = list(messages)
        if len(new_messages) > 1:
            new_messages.insert(1, live_notice)
        else:
            new_messages.append(live_notice)
        return new_messages


def json_dumps_safe(obj: Any) -> str:
    """dump with braces escaped so the LLM output isn't treated as prompt vars."""
    import json

    return json.dumps(obj, indent=2).replace("{", "{{").replace("}", "}}")