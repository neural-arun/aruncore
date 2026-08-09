# 🎯 GOAL.MD — ArunCore Production Upgrade Roadmap & Master Plan

> **STATUS**: 📜 **MASTER EXECUTION SPECIFICATION**
> **PROJECT**: **ArunCore Multi-Tenant Enterprise AI Platform**

---

## 📋 Executive Objective & Mission Statement

The primary goal of this project is to upgrade **ArunCore** into a production-grade, domain-generic, multi-tenant enterprise AI platform while adhering strictly to three non-negotiable directives:

1. 🥇 **100% Frontend Preservation**: The existing Next.js frontend UI layout, components, header, tabs (`ChatPanel`, `ProjectsView`, `ManifestoView`), glowing accent borders, light/dark themes, hero assistant card, and design tokens stay **100% INTACT**. No layout rewrites or UI structural replacements will take place.
2. 🥈 **Zero Functionality Loss (Keep & Enhance Everything)**: Absolutely **NO** working features will be removed from the current app. All existing capabilities—including the Hybrid RAG engine, Telegram active learning alerts, 3-way live human chat presence notice, TTS neural voice endpoints, admin mode, and session history—will be preserved 100% and upgraded for production-grade scaling!
3. 🥉 **Production-Grade Hybrid RAG Engine**: The RAG retrieval pipeline (dense ChromaDB vector search + sparse BM25 keyword search + Cohere/LLM reranking) will be enhanced to deliver hyper-fast, accurate, context-aware answers per tenant.
4. 🏅 **Ultra-Simple Demo Mode (`?tutor=ed_donner` / `?client=ed_donner`)**: Demo mode operates by passing a URL query parameter (`?tutor=ed_donner`). The frontend fetches metadata from `/api/v1/config?tutor=ed_donner` (or `/config?tutor=ed_donner`), which dynamically populates the existing hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt.

---

## 🏛️ The 11 Golden Architecture Principles (NON-NEGOTIABLE)

1. 🥇 **Preserve Current Frontend 100%**: Absolutely DO NOT replace or alter the existing Next.js frontend UI (`frontend/app/page.tsx`, `frontend/components/ChatPanel.tsx`, `ProjectsView.tsx`, `ManifestoView.tsx`, `Header.tsx`). The existing luxury UI, design tokens, glowing accent borders, light/dark themes, hero assistant card, and tab views stay 100% intact!
2. 🥈 **Zero Functionality Loss (Keep & Enhance)**: DO NOT remove a single working feature from the current app (Hybrid RAG, Telegram active learning alerts, 3-way live human chat presence, TTS neural voice, admin mode, session history). The goal is to keep 100% of existing functionality and upgrade it to production grade!
3. 🥉 **Production-Grade Hybrid RAG Engine**: Maintain and enhance the hybrid RAG architecture (dense ChromaDB vector search + sparse BM25 keyword search + Cohere/LLM reranking) for ultra-fast, high-precision knowledge retrieval per tenant.
4. 🏅 **Ultra-Simple Demo System**: Demo mode operates by passing a URL query parameter (`?tutor=ed_donner` or `?client=ed_donner`). The frontend fetches metadata from `/api/v1/config?tutor=ed_donner` (or `/config?tutor=ed_donner`), which dynamically populates the existing hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt. Zero complex slot engines required!
5. 🏅 **Explicit `tenants/` Directory**: All raw PDFs, markdown files, avatars, logos, and vector databases live in `./tenants/` outside the Git code repo. Keep code repos lightweight (~10MB).
6. 🏅 **Split Targeted Config**: Tenant configs in `tenants/<id>/config/` are split into 6 targeted JSON files (`brand.json`, `agent.json`, `chat.json`, `voice.json`, `seo.json`, `social.json`). Easy debugging, zero merge conflicts, Pydantic validated.
7. 🏅 **ZERO Backend Client `if` Statements**: Absolutely NO `if client == "ed":` or `if tenant_id == "hitesh":` statements anywhere in Python code! All tenant logic, prompts, tools, and branding MUST be resolved dynamically by `TenantService`.
8. 🏅 **Config-Driven Tool Registry**: Client tools are controlled via the `enabled_tools` array in `agent.json` (`["search_courses", "book_calendar", "faq_lookup"]`). `ToolExecutor` dynamically binds enabled tools into the LLM execution loop—zero Python code edits required!
9. 🏅 **Separation of Tenant Assets**: Static brand images (`tenants/<id>/assets/avatars/`, `tenants/<id>/assets/logos/`) are kept separate from code logic.
10. 🏅 **Decoupled Single-Responsibility Services**: Maintain small, focused backend services (`PromptBuilder`, `MemoryManager`, `ToolExecutor`, `AgentRunner`, `RAGService`, `NotificationService`, `ActiveLearningService`). Do NOT create monster monolithic service files.
11. 🏅 **Interface Abstractions**: Use abstract base classes for adapters (`VectorStore`, `StateStore`, `NotificationProvider`). Never hardcode direct dependencies in business logic.

---

## 🛠️ Step-by-Step Execution Plan (Detailed Roadmap)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Detailed Step-by-Step Process                         │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│ STEP 1       │ STEP 2       │ STEP 3       │ STEP 4       │ STEP 5          │
│ tenants/     │ Pydantic     │ Decoupled    │ Versioned    │ Testing &       │
│ Directory &  │ Validation   │ Services     │ API Routers  │ Verification    │
│ Split Configs│ Schemas      │ Architecture │ (/api/v1/)   │                 │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────────┘
```

### 📍 Step 1: Explicit `tenants/` Directory & Split Targeted Configs
- Create `./tenants/` root directory structure outside Git.
- Build `tenants/tenant_starter/` and `tenants/ed_donner/` with 6 split JSON configs:
  - `brand.json`: Hero title, role subtitle, avatar path, accent color.
  - `agent.json`: System prompt, guardrails, `enabled_tools` array.
  - `chat.json`: Welcome message, suggested question chips.
  - `voice.json`: TTS alloy voice specs.
  - `seo.json`: Meta title & description.
  - `social.json`: LinkedIn, X, Udemy links.

### 📍 Step 2: Pydantic Validation Schemas (`backend/app/schemas/`)
- Create Pydantic models:
  - `tenant.py`: Validates all 6 tenant JSON configs on load.
  - `chat.py`: Validates `ChatRequest`, streaming NDJSON chunks, session history.
  - `webhook.py`: Validates Telegram/WhatsApp active learning replies.
  - `voice.py`: Validates `TTSRequest` and STT response schemas.

### 📍 Step 3: Decoupled Single-Responsibility Services (`backend/app/services/`)
- Build decoupled Python services preserving 100% of existing functionality:
  - `tenant_service.py`: Dynamic loader for `tenants/<id>/config/` with **ZERO backend `if client == ...` statements**.
  - `prompt_builder.py`: Synthesizes dynamic system prompts, guardrails, bio rules, and 3-way live human chat presence notices.
  - `memory_manager.py`: Manages rolling chat session window context.
  - `tool_executor.py`: Dynamic sandbox for tools specified in `agent.json` (`enabled_tools`).
  - `agent_runner.py`: Handles 100% AI agent control and token-by-token streaming response generation.
  - `rag_service.py`: Hybrid ChromaDB vector search + BM25 keyword search coordinator with reranking.
  - `notification_service.py`: Async Telegram & WhatsApp alert dispatcher.
  - `active_learning_service.py`: Real-time Q&A vector re-ingestion service.

### 📍 Step 4: Interface Adapters (`backend/app/db/`)
- Implement abstract base classes and adapters:
  - `interfaces.py`: Abstract classes (`VectorStore`, `StateStore`, `NotificationProvider`).
  - `vectorstore.py`: ChromaDB + BM25 hybrid implementation.
  - `state_store.py`: Thread-safe session memory store implementation.

### 📍 Step 5: Versioned API Routers (`backend/app/api/v1/`)
- Implement FastAPI versioned routers:
  - `router.py`: Master v1 aggregator.
  - `chat.py`: Streaming `/api/v1/chat`, `/chat/history`, `/chat/human-messages`.
  - `config.py`: Dynamic metadata endpoint `/api/v1/config` (powers `?tutor=ed_donner`).
  - `webhook.py`: Telegram & WhatsApp active learning reply webhooks.
  - `voice.py`: `/api/v1/voice/tts` neural audio generation.

### 📍 Step 6: Frontend Metadata Wiring & Demo Mode Integration
- Connect Next.js frontend (`frontend/app/page.tsx`) to fetch metadata from `/api/v1/config?tutor=ed_donner`.
- Dynamically update hero title, role subtitle, avatar, welcome text, suggested questions, and AI prompt while **preserving 100% of the existing luxury UI layout, tabs, and components**.

### 📍 Step 7: Automated Test Suite & Verification (`tests/`)
- Create test suite in `tests/`:
  - `test_schemas.py`: Verifies Pydantic schema validation.
  - `test_tenant_service.py`: Verifies dynamic tenant loading.
  - `test_chat_api.py`: Verifies streaming responses and endpoint contracts.
- Gather concrete empirical runtime verification.

---

## 🎯 Verification Criteria for Success (Definition of "DONE")

- [ ] Existing Next.js frontend UI layout, components, tabs, and design system are 100% preserved.
- [ ] 100% of current functionality (Hybrid RAG, Telegram active learning alerts, TTS, 3-way live human chat, admin mode) remains fully functional.
- [ ] Hybrid RAG retrieval (ChromaDB + BM25 + Cohere reranking) is enhanced and production-ready per tenant.
- [ ] Demo mode (`?tutor=ed_donner`) dynamically populates hero card metadata and AI system prompt.
- [ ] Backend contains ZERO `if client == "..."` checks anywhere in Python code.
- [ ] `tenants/` storage structure holds isolated client data outside Git code repo.
- [ ] All automated tests pass (`python3 -m unittest discover -s tests`).
- [ ] `aruncore_master_blueprint.md` and `AGENTS.md` match the diff.
