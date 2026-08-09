"""Agent execution loop (the ReAct harness).

Runs the recursive tool-call loop for the ArunCore digital twin: request ->
optional escalation -> up to N tool iterations -> token-by-token streaming of
the final synthesis. Also owns the 3-way live human takeover answer trigger.
This is where the previous `/chat` monolith body now lives, fully reusable by
the FastAPI layer, the Telegram bot vector, and future channels.
"""
import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from langchain_core.messages import SystemMessage

from backend.app.services.session_store import SessionStore, session_store
from backend.app.services.prompt_builder import PromptBuilder


def run_pre_escalation(user_input: str, tool_map: dict, user_metadata: Optional[dict] = None, fast: bool = False) -> Dict[str, Any]:
    """Checks for direct-contact intent that should immediately ping Arun."""
    lowered = (user_input or "").lower()
    urgent_keywords = [
        "hire", "contact", "talk to arun", "call arun", "meet arun",
        "whatsapp", "urgent", "consult", "project inquiry", "work together",
    ]

    for kw in urgent_keywords:
        if kw in lowered:
            return {"escalate": True, "reason": f"Urgent contact keyword detected: '{kw}'"}

    return {"escalate": False, "reason": ""}


class AgentRunner:
    """Orchestrates agentic streaming responses for a single chat request."""

    def __init__(
        self,
        store: Optional[SessionStore] = None,
        agent_factory: Any = None,
        max_iterations: int = 7,
        max_search_limit: int = 7,
    ):
        self.store = store or session_store
        self.agent_factory = agent_factory
        self.max_iterations = max_iterations
        self.max_search_limit = max_search_limit

    async def stream_chat(
        self,
        session_id: str,
        message: str,
        tutor_id: Optional[str] = None,
        tool_map: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yields NDJSON-able chunks: {'type': status|token|final|error}."""
        thoughts: List[str] = []
        try:
            from backend.app.services.notification_service import (
                queue_debug_event,
                queue_maybe_notify_arun,
                queue_chat_history_to_telegram,
                queue_automated_chat_alert,
            )

            if self.agent_factory is None:
                from backend.app.core.agent import init_agent

                self.agent_factory = init_agent

            self.store.record_message(session_id, "user", message)

            queue_debug_event(
                "user_message",
                message,
                {"channel": "api", "session_id": session_id, "tutor_id": tutor_id},
            )

            # 3-way live chat takeover: real Arun is in control, AI Twin pauses.
            if self.store.is_human_control(session_id):
                queue_automated_chat_alert(
                    session_id=session_id,
                    user_input=message,
                    assistant_response="[Real Arun is currently in live control of this chat session. AI Twin paused.]",
                )
                yield {"type": "status", "content": "🟢 Real Arun is in control of this session. AI Twin paused. Waiting for Real Arun or /answer command..."}
                yield {
                    "type": "final",
                    "reply": "",
                    "thoughts": ["Real Arun in live control. AI Twin paused."],
                    "session_id": session_id,
                }
                return

            yield {"type": "status", "content": "Analyzing request & retrieving context..."}
            thoughts.append("Analyzing request & retrieving context...")

            pre_result = run_pre_escalation(message, tool_map or {})
            if pre_result.get("escalate"):
                yield {"type": "status", "content": "Triggering instant Telegram alert..."}
                thoughts.append("Triggering instant Telegram alert...")
                queue_maybe_notify_arun(
                    user_input=message,
                    reason=pre_result.get("reason"),
                    channel="api",
                    session_id=session_id,
                )

            session_llm, session_prompt, _, _ = self.agent_factory(tutor_id=tutor_id)
            memory = self.store.get_or_create_memory(session_id)

            scratchpad: List[Any] = []
            iterations = 0
            search_count = 0
            final_response = ""
            executed_tools: List[str] = []
            retrieved_chunks: List[str] = []
            github_data: List[str] = []

            while iterations < self.max_iterations:
                messages = session_prompt.format_messages(
                    running_summary=memory.running_summary,
                    chat_history=memory.get_messages(),
                    input=message,
                    agent_scratchpad=scratchpad,
                )

                # Inject dynamic Real Human Presence notice if the real human is active.
                arun_human_msgs = self.store.get_human_entries(session_id)
                if arun_human_msgs:
                    messages = PromptBuilder.inject_live_human_notice(messages, arun_human_msgs)

                ai_msg = await asyncio.to_thread(session_llm.invoke, messages)

                if ai_msg.tool_calls:
                    scratchpad.append(ai_msg)
                    for tc in ai_msg.tool_calls:
                        tool_name = tc["name"]
                        tool_args = tc.get("args", {})

                        status_msg = (
                            "Searching Arun's knowledge base..." if tool_name == "search_arun_knowledge"
                            else "Sending notification to Arun..." if tool_name == "notify_arun"
                            else f"Executing {tool_name}..."
                        )

                        yield {"type": "status", "content": status_msg}
                        thoughts.append(status_msg)
                        executed_tools.append(f"{tool_name}({tool_args})")

                        if tool_name == "search_arun_knowledge":
                            search_count += 1

                        if search_count > self.max_search_limit:
                            tool_result = f"Search limit reached ({self.max_search_limit}). Finalizing based on existing context."
                        else:
                            tool_func = (tool_map or {}).get(tool_name)
                            tool_result = await asyncio.to_thread(tool_func.invoke, tool_args) if tool_func else f"Unknown tool: {tool_name}"

                        if tool_name == "search_arun_knowledge" and tool_result:
                            retrieved_chunks.append(str(tool_result)[:1000])
                        elif tool_name == "get_github_live_data" and tool_result:
                            github_data.append(str(tool_result)[:1000])

                        scratchpad.append({
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tc["id"],
                            "content": str(tool_result)[:15000],
                        })
                    iterations += 1
                else:
                    yield {"type": "status", "content": "Synthesizing final response..."}
                    thoughts.append("Synthesizing final response...")

                    full_reply = ""
                    async for chunk in self._stream_tokens(session_llm, messages):
                        yield chunk
                        if isinstance(chunk, dict) and chunk.get("type") == "token":
                            full_reply += chunk["content"]

                    final_response = full_reply
                    break

            if not final_response:
                yield {"type": "status", "content": "Synthesizing final response..."}
                thoughts.append("Synthesizing final response...")
                messages_fallback = session_prompt.format_messages(
                    running_summary=memory.running_summary,
                    chat_history=memory.get_messages(),
                    input=message,
                    agent_scratchpad=scratchpad,
                )
                full_reply = ""
                async for chunk in self._stream_tokens(session_llm, messages_fallback):
                    yield chunk
                    if isinstance(chunk, dict) and chunk.get("type") == "token":
                        full_reply += chunk["content"]
                final_response = full_reply

            memory.add_interaction(message, final_response)
            self.store.record_message(session_id, "twin", final_response, thoughts=thoughts)

            queue_chat_history_to_telegram(
                session_id=session_id,
                user_input=message,
                assistant_response=final_response,
                thoughts=thoughts,
                tool_calls=executed_tools,
                retrieved_chunks=retrieved_chunks,
                github_data=github_data,
            )

            # Unconditionally queue 100% automated chat alert for EVERY chat.
            queue_automated_chat_alert(
                session_id=session_id,
                user_input=message,
                assistant_response=final_response,
            )

            yield {
                "type": "final",
                "reply": final_response,
                "thoughts": thoughts,
                "session_id": session_id,
            }

        except Exception as err:
            err_msg = f"API Error: {str(err)}"
            yield {"type": "error", "content": err_msg}

    async def trigger_ai_answer(self, session_id: str, extra_prompt: str = "") -> str:
        """Synthesize an AI answer after the /answer command from the real human."""
        from backend.app.core.agent import init_agent

        memory = self.store.get_or_create_memory(session_id)
        main_llm, prompt, _, _ = init_agent()

        session_msgs = self.store.get_history(session_id)
        transcript_lines = []
        last_user_input = ""
        for m in session_msgs:
            sender_label = (
                "Visitor" if m.get("sender") == "user"
                else "Real Arun Yadav (👨‍💻)" if m.get("sender") == "human_arun"
                else "Arun's AI Assistant"
            )
            transcript_lines.append(f"{sender_label}: {m.get('text')}")
            if m.get("sender") == "user":
                last_user_input = m.get("text")

        full_transcript = "\n".join(transcript_lines)

        system_notice = SystemMessage(content=(
            f"🟢 3-WAY CHAT INSTRUCTION FOR AI TWIN:\n"
            f"Real Arun Yadav issued the /answer command for you to respond to the visitor's question.\n"
            f"Read the full 3-party conversation transcript below (Visitor, Real Arun Yadav, and AI Twin):\n\n"
            f"--- FULL 3-WAY CHAT TRANSCRIPT ---\n{full_transcript}\n\n"
            f"MANDATORY INSTRUCTIONS FOR AI TWIN:\n"
            f"1. Synthesize all context from the visitor's question and Real Arun Yadav's live comments.\n"
            f"2. Generate an accurate, helpful, and natural response for the visitor.\n"
            f"3. Acknowledge Real Arun Yadav's live presence if relevant."
        ))

        messages = prompt.format_messages(
            running_summary=memory.running_summary,
            chat_history=memory.get_messages(),
            input=extra_prompt or last_user_input or "Please answer the visitor's question based on our 3-way conversation.",
            agent_scratchpad=[],
        )
        messages.insert(1, system_notice)

        ai_msg = await asyncio.to_thread(main_llm.invoke, messages)
        final_reply = ai_msg.content.strip()

        if final_reply:
            self.store.record_message(
                session_id, "twin", final_reply,
                thoughts=["AI Twin triggered via /answer command."],
            )
            memory.add_interaction(last_user_input or "Visitor Query", final_reply)

        return final_reply

    async def _stream_tokens(self, llm, messages):
        """Yields {'type':'token', 'content': ...} chunks by streaming the LLM.

        Mirrors the original implementation: the sync `llm.stream` generator is
        consumed in place so tokens arrive incrementally over the wire.
        """
        for chunk in llm.stream(messages):
            if getattr(chunk, "content", None):
                yield {"type": "token", "content": chunk.content}
                await asyncio.sleep(0.005)

    def sync_reply(
        self,
        session_id: str,
        user_input: str,
        llm: Any,
        prompt: Any,
        memory: Any,
        tool_map: Optional[Dict[str, Any]] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
        max_iterations: int = 3,
    ) -> str:
        """Blocking agent turn for non-streaming channels (Telegram bot).

        Replicates the legacy bot loop exactly (3 iterations, tool errors
        swallowed into the reply context, final fallback message).
        """
        from backend.app.services.notification_service import (
            queue_debug_event,
            queue_maybe_notify_arun,
        )

        scratchpad: List[Any] = []
        tool_map = tool_map or {}

        try:
            queue_debug_event(
                "user_message",
                user_input,
                {"channel": "telegram", "chat_id": session_id, **(user_metadata or {})},
            )

            pre_escalation = run_pre_escalation(
                user_input,
                tool_map,
                {"channel": "telegram", "chat_id": session_id, **(user_metadata or {})},
                False,
            )
            if pre_escalation:
                queue_debug_event(
                    "pre_escalation",
                    pre_escalation.get("result", ""),
                    {
                        "channel": "telegram",
                        "chat_id": session_id,
                        "category": pre_escalation.get("category"),
                        "reason": pre_escalation.get("reason"),
                        **(user_metadata or {}),
                    },
                )

            final_response = None

            for _ in range(max_iterations):
                messages = prompt.format_messages(
                    running_summary=memory.running_summary,
                    chat_history=memory.get_messages(),
                    input=user_input,
                    agent_scratchpad=scratchpad,
                )
                ai_msg = llm.invoke(messages)

                if ai_msg.tool_calls:
                    scratchpad.append(ai_msg)
                    for tc in ai_msg.tool_calls:
                        tool_name = tc["name"]
                        tool_args = tc.get("args", {})
                        queue_debug_event(
                            "tool_call",
                            json.dumps(tool_args, ensure_ascii=False, indent=2, default=str),
                            {
                                "channel": "telegram",
                                "chat_id": session_id,
                                "tool_name": tool_name,
                                **(user_metadata or {}),
                            },
                        )

                        tool_func = tool_map.get(tool_name)
                        try:
                            result = tool_func.invoke(tool_args)
                        except Exception as e:
                            result = f"Tool error: {e}"

                        scratchpad.append({
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tc["id"],
                            "content": str(result)[:2000],
                        })
                        queue_debug_event(
                            "tool_result",
                            str(result),
                            {
                                "channel": "telegram",
                                "chat_id": session_id,
                                "tool_name": tool_name,
                                **(user_metadata or {}),
                            },
                        )
                else:
                    final_response = ai_msg.content
                    break

            if not final_response:
                final_response = "I ran into an issue internally. Please try again."

            queue_debug_event(
                "assistant_reply",
                final_response,
                {"channel": "telegram", "chat_id": session_id, **(user_metadata or {})},
            )

            queue_maybe_notify_arun(
                user_input=user_input,
                final_response=final_response,
                scratchpad=scratchpad,
                tool_map=tool_map,
                user_metadata={"channel": "telegram", "chat_id": session_id, **(user_metadata or {})},
                pre_notified=bool(pre_escalation and pre_escalation.get("handled")),
            )

            memory.add_interaction(user_input, final_response)
            return final_response
        except Exception as e:
            queue_debug_event(
                "error",
                str(e),
                {"channel": "telegram", "chat_id": session_id, **(user_metadata or {})},
            )
            raise


agent_runner = AgentRunner(agent_factory=None)