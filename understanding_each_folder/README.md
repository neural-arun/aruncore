# 📚 Understanding Each Folder — ArunCore Technical Guides

> Walkthrough files for every major folder. Read this BEFORE modifying code.
> Architecture version: ❄️ v1.0 (decoupled services backend).

---

## 🧭 Fast Path (5-minute overview)

```
ArunVisitor ─▶ core/api.py (thin FastAPI) ─▶ services/agent_runner.py
                                                 │ running)
                                                 ├▶ services/prompt_builder.py   (system prompt + templates)
                                                 ├▶ services/memory_manager.py   (RollingMemory compression)
                                                 ├▶ services/tool_executor.py    (real tools: search/github/notify)
                                                 ├▶ services/knowledge_service.py(READMEs, LinkedIn, static, Q&A)
                                                 ├▶ services/notification_service.py (Telegram + background queue)
                                                 └▶ services/session_store.py    (thread-safe live state)
```

**Golden rule**: Tools/chat/branding logic MUST live in `services/` modules and resolve
dynamically. `backend/app/core/` only composes (agent.py) and wires HTTP (api.py).
Zero `if client == "..."` anywhere.

---

## 📂 backend/app/core/ — Composition & Channels (thin)

- **agent.py** — The only *allowed* place that imports everything. Exposes `init_agent()` (returns `(main_llm, chat_prompt, memory, tools)`) plus backward-compat re-exports (`queue_*`, `save_unknown_question_answer`, `RollingMemory`, tools, admin tokens) so scripts/tests/bot keep working. Also applies the IPv4-only DNS patch once.
- **api.py** — FastAPI wiring only: CORS, models, `/chat` (delegates to `AgentRunner.stream_chat`), `/config`, `/tts`, `/chat/human-message`, `/chat/history`, `/chat/human-messages`, `/chat/verify-admin-token`, `/health`, static frontend mount. **No business logic.**
- **bot.py** — Telegram bot entrypoint. Reuses `AgentRunner.sync_reply` for the agent loop and `knowledge_service.save_verified_answer` for the reply-to-save active-learning flow.
- **ingest.py** — Standalone ChromaDB ingestion (`data/` → `db/`), idempotent via `db/ingestion_state.json`.

## 📂 backend/app/services/ (Single-Responsibility — the real brains)

| Service | Owns |
|---|---|
| `agent_runner.py` | Streaming agent loop, `run_pre_escalation`, `trigger_ai_answer` (`/answer`), `sync_reply` (Telegram). |
| `prompt_builder.py` | Static-context 5-tuple, tutor (legacy demos) vs default persona prompt, chat template, 3-way live human notice. |
| `memory_manager.py` | `RollingMemory` (every-N-turn summary compression) + `MemoryManager` alias. |
| `tool_executor.py` | Tool registry: real `search_arun_knowledge`, `get_github_live_data`, `notify_arun` + tenant placeholder tools. |
| `knowledge_service.py` | All on-disk knowledge reads + `fetch_live_github` + `save_verified_answer` (active-learning write + re-ingest trigger). `search()` section-chunks READMEs/LinkedIn/profile docs, strips YAML+GitHub boilerplate, relevance-scores every chunk and caps output → returns clean ranked chunks instead of raw whole files. |
| `rag_service.py` | Hybrid retrieval coordinator → normalizes to scored chunks; `add_knowledge_entry` persists via KnowledgeService. |
| `tenant_service.py` | Split `tenants/<id>/config/*.json` (Pydantic validated) + legacy `demos/*.json` loader. |
| `notification_service.py` | Every Telegram send (relay→direct→plain fallback), alert dedup, chat-log/debug/automated alerts, `notify_arun` escalation. |
| `session_store.py` | Thread-safe message history, human-messages, human-control flags, rolling memory per session. |
| `auth_service.py` | `generate_admin_token` / `verify_admin_token` (3-way live takeover). |
| `background.py` | One shared background worker queue used by notification/knowledge tasks. |
| `active_learning_service.py` | Owner-reply ingestion (webhook → RAGService → unknown_questions.json + ChromaDB). |
| `voice_service.py` | OpenAI TTS audio generation. |

## 📂 backend/app/schemas/ — Pydantic contracts
`tenant.py` (6 split configs + `TenantFullConfig.to_legacy_dict`), `chat.py` (`ChatRequest`, history, NDJSON chunk), `webhook.py` (active-learning payload), `voice.py` (`TTSRequest`).

## 📂 backend/app/db/ — Interface adapters
`interfaces.py` — abstract `VectorStoreInterface`, `StateStoreInterface`, `NotificationProviderInterface`.
`state_store.py` — the in-memory `StateStore` implementation (session message log used by legacy paths).

## 📂 backend/app/api/v1/ — Versioned routers
`config.py` (`/api/v1/config` → split tenants), `voice.py` (`/tts`), `webhook.py`, `router.py` aggregator.

## 📂 frontend/ — Next.js 16 UI (100% PRESERVED)
`page.tsx` fetches `/api/config/tutor` config, streams NDJSON, polls `/chat/history` (1.5s), admin/3-way mode via join-link token. Files under `components/` are the luxury UI: `ChatPanel`, `Header`, `Sidebar`, `ProjectsView`, `ManifestoView`, `HandoffModal`, `MobileBottomNav`, `TelemetryPanel`, `ArchitectureView`.

## 📂 data/ (knowledge base)
`github/<repo>/README.md` (21 repos) · `linkedin/posts.md` · `raw/personal_background.md` · `raw/unknown_questions.json` (active learning) · `static/*.md` (public_profile, rules_of_engagement).

## 📂 tenants/ — Split-config tenant packages (OUTSIDE apt / S3)
`tenants/<id>/config/{brand,agent,chat,voice,seo,social}.json`. `tenant_starter/` is the fallback template.

## 📂 demos/ & data/leads/ — legacy 238-key dictionaries
`demos/*_enterprise_dictionary.json` + `demos/general.json` (master template). Resolved via `tenant_service.load_legacy_tutor_config`.

## 🧪 tests/
`unittest discover -s tests` → 9 passing tests (schemas, v1 config, tenants, API endpoints). `tests/test_system.py` is a manual 5-part integration script (uses network/LLM/Telegram).

## 📜 scripts/
`evaluate.py`, `evaluate_30_questions.py` (agent stress tests), `ingest.py`, `sync_github.py`, `sync_linkedin.py`, `sync_all.py`.

---

## 🔄 Decoupling rules of thumb

- Want to change how alerts deliver? Touch `notification_service.py` only.
- Want to add a tool? Register it in `tool_executor.py` (`AVAILABLE_TOOLS`).
- Want a new KB source? Update `knowledge_service.py` search fan-out.
- Want to change memory strategy? Swap logic in `memory_manager.py` — keep `RollingMemory` name for compat.
- Never import `core/api.py` symbols into a service; services are the dependency root underneath `core/*`.