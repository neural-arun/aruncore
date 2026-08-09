# ⚙️ ArunCore Backend Architecture (`backend/`)

> **Architecture Spec:** Decoupled Single-Responsibility Services  
> **Framework:** FastAPI / Uvicorn  
> **LLM Engine:** `gpt-4.1-nano` (via LangChain `ChatOpenAI`)  
> **RAG Engine:** ChromaDB + BM25 + Cohere English V3 Reranker  

---

## 📁 Backend Directory Map

```text
backend/app/
├── api/v1/                   # REST API Endpoints & Webhooks
│   ├── config.py             # GET /api/v1/config (238-key enterprise JSON resolver)
│   ├── router.py             # Main API Router
│   ├── voice.py              # POST /api/v1/voice/speak & audio STT endpoint
│   └── webhook.py            # POST /api/v1/webhook (Telegram live takeover webhook)
├── core/                     # Agent Orchestration Core
│   ├── agent.py              # LLM init, search_arun_knowledge, get_github_live_data, notify_arun
│   ├── api.py                # Legacy API handler compatibility layer
│   ├── bot.py                # Telegram bot delivery helpers
│   ├── evaluate.py           # Core evaluation functions
│   └── ingest.py             # Local vector store ingestion module
├── schemas/                  # Pydantic Schemas & Data Contracts
│   ├── chat.py               # ChatRequest, ChatResponse
│   ├── tenant.py             # TenantConfig schema
│   ├── voice.py              # VoiceSpeakRequest, VoiceSpeakResponse
│   └── webhook.py            # TelegramWebhookPayload
├── services/                 # Decoupled Business Logic Services
│   ├── active_learning_service.py # Unknown question logger & memory saver
│   ├── memory_manager.py     # RollingMemory summary compression engine
│   ├── notification_service.py # Telegram alert queue & delivery service
│   ├── prompt_builder.py     # Dynamic System Prompt assembler
│   ├── rag_service.py        # Hybrid Vector Search + BM25 + Reranker pipeline
│   ├── tenant_service.py     # Dynamic JSON config loader (Zero backend `if` checks)
│   ├── tool_executor.py      # Config-driven tool binder & execution loop
│   └── voice_service.py      # OpenAI tts-1 audio synthesizer
└── main.py                   # FastAPI Application Entrypoint
```

---

## 🔌 Primary API Endpoints

### 1. `GET /api/v1/config?tutor=<tutor_id>`
- Resolves tenant configuration dynamically from `demos/<tutor_id>_enterprise_dictionary.json`.
- Returns full 238-key JSON payload including `theme_design_system`, `frontend_ui_dictionary`, `courses`, and `custom_system_prompt`.

### 2. `POST /chat` / `POST /api/v1/chat`
- Accepts user messages and executes the 7-iteration ReAct tool loop (`search_arun_knowledge`, `get_github_live_data`, `notify_arun`).
- Streams or returns the final response along with tool execution traces.

### 3. `POST /api/v1/voice/speak`
- Synthesizes text into natural studio neural speech audio using OpenAI `tts-1` (`alloy` voice).

---

## 🧪 Testing Backend Services

Run all backend test cases:
```bash
python3 -m unittest discover -s tests
```
