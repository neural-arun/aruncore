from typing import List, Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from backend.app.schemas.tenant import TenantFullConfig


class PromptBuilder:
    @staticmethod
    def build_system_prompt(config: TenantFullConfig, static_profile: str = "", static_rules: str = "") -> str:
        base_prompt = config.agent.system_prompt
        guardrails_str = "\n".join([f"• {g}" for g in config.agent.guardrails])

        prompt_parts = [
            base_prompt,
            f"\n\n--- INSTRUCTOR / CLIENT PROFILE ---\n{static_profile}" if static_profile else "",
            f"\n\n--- RULES OF ENGAGEMENT ---\n{static_rules}" if static_rules else "",
            f"\n\n--- MANDATORY GUARDRAILS ---\n{guardrails_str}" if guardrails_str else "",
            f"\n\nWelcome Message: \"{config.chat.welcome_message}\""
        ]

        return "\n".join([p for p in prompt_parts if p.strip()])

    @staticmethod
    def build_chat_prompt_template(system_prompt_text: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}\n\nRunning Context Summary:\n{running_summary}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]).partial(system_prompt=system_prompt_text)

    @staticmethod
    def inject_live_human_notice(messages: List[Any], arun_human_msgs: List[Dict[str, Any]]) -> List[Any]:
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
