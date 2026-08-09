# 🏛️ ArunCore — Master Enterprise AI System Blueprint & Architecture Specification (v1.0 Frozen)

> **STATUS**: ❄️ **ARCHITECTURE v1.0 FROZEN** (Official Release Specification)

## 📋 Executive Overview & System Philosophy

**ArunCore** is a production-grade, stateful, agentic portfolio and multi-tenant enterprise AI engine platform created by **Arun Yadav** (AI Systems Architect specializing in Healthcare & Education).

**ArunCore** operates on a **Domain-Generic Engine Architecture** with **100% Preservation of Arun's Existing Next.js Frontend UI** and **Zero Loss of Existing Capabilities**. The **AI Agent stays in control 100% of the time**. Instead of complex live web page human takeovers, **ArunCore** relies on a high-precision **Hybrid RAG Engine** and an **Active Learning & Direct Messaging Loop (Telegram / WhatsApp)**:
- **Hybrid RAG Retrieval**: Combines dense vector search (ChromaDB), sparse keyword search (BM25), and Cohere/LLM reranking to deliver hyper-accurate, context-aware answers per tenant.
- **Active Learning Loop**: When a visitor asks an unknown, personal, weird, or low-confidence question, the AI Twin responds politely and alerts the owner on Telegram/WhatsApp with a 1-Click reply link.
- **Real-Time Vector Ingestion**: The owner replies directly in Telegram/WhatsApp, automatically ingesting the answer into ChromaDB in real time to train the AI Twin instantly for all future visitors!
- **3-Way Live Chat Presence**: When the owner joins a live session via Telegram, the AI system prompt dynamically injects a 3-way chat notice acknowledging the human instructor's live presence alongside the AI assistant.

### The Business & Product Model:
1. **Ultra-Simple Demo Mode (`?tutor=ed_donner` / `?client=ed_donner`)**: Instant data-driven client demos for 2-minute sales pitch videos to potential buyers. Passing `?tutor=ed_donner` in the URL fetches `/api/v1/config?tutor=ed_donner` (or `/config?tutor=ed_donner`), which dynamically updates the hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt on Arun's existing stunning UI!
2. **Paid Client Onboarding ($300 – $1,000+ Tier)**: Rapid 5-minute onboarding of custom AI twins for tutors, instructors, doctors, lawyers, or consultants, with zero code duplication, zero backend `if client == ...` statements, zero frontend UI changes, and 100% isolated tenant data in `tenants/`.

---

## 🎯 The 11 Senior Systems Architect Principles

```
  🥇 1. Preserve Current Frontend 🥈 2. Zero Functionality Loss  🥉 3. Production Hybrid RAG   🏅 4. Ultra-Simple Demos
  (Keep page.tsx, ChatPanel,     (Keep RAG, Telegram alerts,    (ChromaDB + BM25 + Cohere     (?tutor=ed_donner dynamically
   ProjectsView & Manifesto)      TTS, 3-way live chat notice)   dense/sparse hybrid engine)    updates hero card & prompt)

  🏅 5. Explicit tenants/ Storage 🏅 6. Split Targeted Config   🏅 7. Zero Client Ifs         🏅 8. Config-Driven Tools
  (PDFs, docs & configs in      (brand, agent, chat, voice,    (100% TenantService            (enabled_tools array in
   tenants/ outside Git)        seo, social sub-configs)       dynamic resolution)            agent.json controls tools)

  🏅 9. Separate Tenant Assets  🏅 10. Decoupled Backend       🏅 11. Direct Active Learning
  (tenants/<id>/assets/ logos  (PromptBuilder, ToolExec,      (Owner replies via Telegram,
   & avatars isolated)          MemoryManager, AgentRunner)    auto-ingesting into RAG DB)
```

1. **Preserve Current Frontend 100%**: Absolutely DO NOT replace or alter the existing Next.js frontend UI (`frontend/app/page.tsx`, `frontend/components/ChatPanel.tsx`, `ProjectsView.tsx`, `ManifestoView.tsx`, `Header.tsx`). The existing luxury UI, design tokens, glowing accent borders, light/dark themes, hero assistant card, and tab views stay 100% intact!
2. **Zero Functionality Loss (Keep & Enhance)**: DO NOT remove a single working feature from the current app (Hybrid RAG, Telegram active learning alerts, 3-way live human chat presence, TTS neural voice, admin mode, session history). The goal is to keep 100% of existing functionality and upgrade it to production grade!
3. **Production-Grade Hybrid RAG Engine**: Maintain and enhance the hybrid RAG architecture (dense ChromaDB vector search + sparse BM25 keyword search + Cohere/LLM reranking) for ultra-fast, high-precision knowledge retrieval per tenant.
4. **Ultra-Simple Demo System**: Demo mode operates by passing a URL query parameter (`?tutor=ed_donner` or `?client=ed_donner`). The frontend fetches metadata from `/api/v1/config?tutor=ed_donner` (or `/config?tutor=ed_donner`), which dynamically populates the existing hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt. Zero complex slot engines required!
5. **Explicit `tenants/` Storage**: All raw PDFs, markdown files, avatars, logos, and vector databases live in `./tenants/` outside the Git code repo. Keeps `git clone` lightweight (~10MB), enables fast deployments, self-documents tenant data isolation, and allows seamless S3/Cloudflare R2 sync.
6. **Split Targeted Config**: Instead of one monolithic 238-key `config.json`, tenant configuration is divided into targeted JSON files (`brand.json`, `agent.json`, `chat.json`, `voice.json`, `seo.json`, `social.json`). Easy debugging, zero merge conflicts, Pydantic validated.
7. **ZERO Backend Client Logic**: No `if client == "ed":` statements anywhere in Python code! All tenant logic is resolved dynamically by `TenantService`.
8. **Config-Driven Tool Registry**: Client tool activation is controlled entirely via `enabled_tools` in `agent.json` (`["search_courses", "book_calendar", "faq_lookup"]`). `ToolExecutor` dynamically registers only enabled tools into the LLM execution loop—zero Python code edits required!
9. **Separation of Tenant Assets & Engine**: Static brand assets (`tenants/<id>/assets/avatars/`, `tenants/<id>/assets/logos/`) are kept separate from code logic.
10. **Decoupled Single-Responsibility Backend Services**: `AgentService` is split into clean micro-services: `PromptBuilder`, `MemoryManager`, `ToolExecutor`, `AgentRunner`, `RAGService`, `NotificationService`, `ActiveLearningService`.
11. **Interface Abstractions**: Abstract base classes for persistence and notification providers (`VectorStore`, `StateStore`, `NotificationProvider`). Swapping ChromaDB to Qdrant, Redis to Memory, or Telegram to WhatsApp takes 1 line of config!

---

## 🏗️ End-to-End System Architecture

```mermaid
graph TD
    subgraph Client & UI Layer (frontend/ - 100% Preserved UI)
        ArunVisitor["Arun Portfolio Visitor<br/>(www.neuralarun.in)"]
        DemoVisitor["Demo / Client Visitor<br/>(?tutor=ed_donner)"]
    end

    subgraph API Gateway Layer (backend/app/api/v1/)
        APIRouter["API Router Aggregator (router.py)"]
        ChatAPI["/api/v1/chat"]
        ConfigAPI["/api/v1/config"]
        VoiceAPI["/api/v1/voice"]
        WebhookAPI["/api/v1/webhook (Telegram / WhatsApp)"]
    end

    subgraph Business Logic Services (backend/app/services/)
        TenantService["Tenant & Config Service"]
        PromptBuilder["Prompt Builder Service"]
        MemoryManager["Rolling Memory Manager (MemoryManager =<br/>RollingMemory alias)"]
        ToolExecutor["Dynamic Config-Driven Tool Executor"]
        AgentRunner["Agent Runner Engine (100% Agent Control)"]
        KnowledgeService["Knowledge Retrieval Service (GitHub +<br/>READMEs + LinkedIn + static + Q&A)"]
        RAGService["Hybrid RAG Coordinator (ChromaDB + BM25)"]
        NotificationService["Telegram / Alert Dispatcher + Background Queue"]
        SessionService["Thread-Safe Session & Memory Store"]
        AuthService["Admin Token Auth (3-Way Live Takeover)"]
        BackgroundQueue["Shared Background Task Queue"]
        ActiveLearningService["Active Learning (owner-answer ingestion)"]
    end

    subgraph Interface Adapters (backend/app/db/ & core/)
        VectorStore["VectorStore Interface<br/>(ChromaDB + BM25 + Cohere)"]
        StateStore["StateStore Interface<br/>(Redis / Thread-Safe Memory)"]
        NotificationProvider["NotificationProvider Interface<br/>(Telegram / WhatsApp API)"]
        CompositionRoot["core/agent.py (thin composition<br/>root: init_agent + facade re-exports)"]
        HTTPLayer["core/api.py (thin FastAPI wiring only)"]
    end

    subgraph Tenant Storage Layer (tenants/)
        TenantConfigs["tenants/<id>/config/<br/>(brand, agent, chat, voice, seo, social)"]
        TenantAssets["tenants/<id>/assets/<br/>(avatars, logos, graphics)"]
        TenantKnowledge["tenants/<id>/knowledge/<br/>(markdown, PDFs, raw data, active_learning.json)"]
    end

    ArunVisitor --> ConfigAPI
    ArunVisitor --> ChatAPI
    DemoVisitor --> ConfigAPI
    DemoVisitor --> ChatAPI
    
    APIRouter --> ChatAPI
    APIRouter --> ConfigAPI
    APIRouter --> VoiceAPI
    APIRouter --> WebhookAPI

    ChatAPI --> AgentRunner
    ConfigAPI --> TenantService
    WebhookAPI --> ActiveLearningService

    AgentRunner --> PromptBuilder
    AgentRunner --> MemoryManager
    AgentRunner --> ToolExecutor
    AgentRunner --> KnowledgeService
    AgentRunner --> RAGService
    AgentRunner --> NotificationService
    AgentRunner --> SessionService
    AgentRunner --> CompositionRoot

    ToolExecutor --> KnowledgeService
    ToolExecutor --> NotificationService

    NotificationService --> BackgroundQueue
    NotificationService --> AuthService
    HTTPLayer --> AgentRunner
    HTTPLayer --> SessionService
    HTTPLayer --> AuthService
    HTTPLayer --> NotificationService
    
    TenantService --> TenantConfigs
    ToolExecutor --> TenantConfigs
    RAGService --> KnowledgeService
    KnowledgeService --> VectorStore
    VectorStore --> TenantKnowledge
    ActiveLearningService --> VectorStore
    ActiveLearningService --> RAGService
    NotificationService --> NotificationProvider
```

---

## 📁 Repository Directory & Tenant Storage Structure

```
aruncore/
├── backend/                      # ⚙️ FASTAPI BACKEND SERVICE
│   ├── app/
│   │   ├── api/                  # 🌐 VERSIONED API ROUTERS (v1)
│   │   │   ├── v1/
│   │   │   │   ├── router.py     # Master v1 API Router Aggregator
│   │   │   │   ├── config.py     # /api/v1/config multi-tenant metadata resolution
│   │   │   │   ├── webhook.py    # Telegram & WhatsApp reply webhook (Active Learning)
│   │   │   │   └── voice.py      # /api/v1/voice/tts neural TTS audio
│   │   │
│   │   ├── schemas/              # 📋 PYDANTIC VALIDATION SCHEMAS
│   │   │   ├── tenant.py         # Sub-config schemas (Brand, Agent, Chat, Voice, SEO, Social)
│   │   │   ├── chat.py           # ChatRequest, ChatHistoryResponse, NDJSONStreamChunk schemas
│   │   │   ├── webhook.py        # Telegram/WhatsApp incoming reply webhook schema
│   │   │   └── voice.py          # TTSRequest schema
│   │   │
│   │   ├── services/             # 🧠 SINGLE-RESPONSIBILITY SERVICES (DECOUPLED)
│   │   │   ├── background.py     # Shared background task queue + worker thread
│   │   │   ├── tenant_service.py # Dynamic tenant + legacy demos config resolver
│   │   │   ├── prompt_builder.py # System prompt, static context & avatar assembly
│   │   │   ├── memory_manager.py # RollingMemory summary-compression + MemoryManager alias
│   │   │   ├── tool_executor.py  # Real tool registry (search / github / notify) + placeholders
│   │   │   ├── agent_runner.py   # Streaming + sync agent loop (7-iters, 3-way live notice)
│   │   │   ├── knowledge_service.py # Reads/writes ALL knowledge data (GitHub, LinkedIn, static, Q&A)
│   │   │   ├── rag_service.py    # Hybrid RAG coordinator + active-learning persistence
│   │   │   ├── notification_service.py # Telegram send/alert/queue/logging + alert dedup
│   │   │   ├── auth_service.py   # Admin token generation + verification
│   │   │   ├── session_store.py  # Thread-safe session / human-control / memory store
│   │   │   ├── active_learning_service.py # owner-reply -> RAG ingestion
│   │   │   └── voice_service.py  # Speech synthesis (TTS)
│   │   │
│   │   ├── db/                   # 🔌 INTERFACE ADAPTERS
│   │   │   ├── interfaces.py     # Abstract Base Classes (VectorStore, StateStore, NotificationProvider)
│   │   │   └── state_store.py    # Thread-Safe In-Memory StateStore Implementation
│   │   │
│   │   ├── core/                 # 🔧 COMPOSITION ROOT, HTTP LAYER & CHANNELS
│   │   │   ├── agent.py          # init_agent factory + IPv4 patch + backward-compat facade
│   │   │   ├── api.py            # Thin FastAPI wiring (/chat, /config, /tts, admin, health)
│   │   │   ├── bot.py            # Telegram bot (uses shared AgentRunner.sync_reply)
│   │   │   └── ingest.py         # ChromaDB knowledge ingestion (data/ -> db/)
│   │   │
│   │   └── main.py               # FastAPI entrypoint (mounts v1 routers)
│   │
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/                     # 🎨 NEXT.JS 16 FRONTEND WEB APP (100% PRESERVED)
│   ├── app/
│   │   ├── page.tsx              # Main App Router (Arun's Portfolio + Dynamic Tenant Metadata Loader)
│   │   ├── layout.tsx            # Global layout provider
│   │   └── globals.css           # Global design tokens & CSS root variables
│   │
│   ├── components/
│   │   ├── ChatPanel.tsx         # Primary Chat Panel & Hero Assistant Card (100% Preserved)
│   │   ├── ProjectsView.tsx      # Projects Portfolio View (100% Preserved)
│   │   ├── ManifestoView.tsx     # Manifesto View (100% Preserved)
│   │   ├── Header.tsx            # Header bar & navigation (100% Preserved)
│   │   └── Sidebar.tsx           # Sidebar navigation (100% Preserved)
│   │
│   ├── hooks/                    # Custom React Hooks
│   ├── lib/                      # Types & API helpers
│   ├── package.json
│   └── tsconfig.json
│
├── tenants/                      # 📦 EXPLICIT TENANT DATA (OUTSIDE GIT REPO / S3 BUCKET)
│   ├── ed_donner/                # Ed Donner Tenant Package
│   │   ├── config/               # 📄 SPLIT CONFIG FILES
│   │   │   ├── brand.json        # Hero title, subtitle, colors, avatar path
│   │   │   ├── agent.json        # System prompt, guardrails, enabled_tools array
│   │   │   ├── chat.json         # Quick questions, welcome message
│   │   │   ├── voice.json        # TTS alloy voice specs
│   │   │   ├── seo.json          # Meta title & description
│   │   │   └── social.json       # Udemy, LinkedIn, X, website links
│   │   ├── assets/               # 🖼️ STATIC ASSETS (avatars, logos, graphics)
│   │   │   ├── avatar.png
│   │   │   └── logo.png
│   │   └── knowledge/            # 📚 RAW KNOWLEDGE (markdown, PDFs, active_learning.json)
│   │       ├── courses.md
│   │       └── active_learning.json
│   │
│   ├── tenant_starter/           # Quick starter template for instant 1-min onboarding
│   └── vector_db/                # Persistent ChromaDB sqlite & vector indexes
│
├── data/                         # 📹 DEMO DATA & GLOBAL PROFILES
│   └── static/                   # Arun's static profile & rules of engagement
│
├── docs/                         # Operational SOPs & Architecture Playbooks
├── scripts/                      # Vector ingestion (`ingest_knowledge.py`), evaluation scripts
├── tests/                        # Automated unit & integration test suites
├── docker-compose.yml            # Multi-container orchestration (Backend + Redis)
├── Makefile                      # Developer workflow commands
└── README.md                     # Master Repository Overview
```

---

## 🎯 Final Master Checklist

- [x] **100% Frontend Preservation**: Existing Next.js frontend UI (`page.tsx`, `ChatPanel.tsx`, `ProjectsView.tsx`, `ManifestoView.tsx`, `Header.tsx`) is preserved 100% with zero layout changes!
- [x] **Zero Functionality Loss**: 100% of existing features (Hybrid RAG, Telegram active learning, TTS, 3-way live human chat notice, admin mode) are retained and upgraded.
- [x] **Production-Grade Hybrid RAG Engine**: ChromaDB dense vector + BM25 sparse keyword search + Cohere/LLM reranking.
- [x] **Ultra-Simple Demo Mode**: Query param `?tutor=ed_donner` dynamically populates hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt.
- [x] **100% AI Agent Control**: Web chat is always handled by the AI Twin. Zero complex live web page human takeovers needed.
- [x] **Direct Active Learning Loop**: Owner replies directly in Telegram or WhatsApp to train their AI Twin in real time.
- [x] **Split Targeted Config**: 6 targeted JSON files (`brand`, `agent`, `chat`, `voice`, `seo`, `social`).
- [x] **Explicit `tenants/` Directory**: External tenant data (`tenants/<id>/config`, `assets`, `knowledge`) isolated outside Git code repo.
- [x] **ZERO Client `if` Statements**: 100% dynamic `TenantService` resolution in backend.
- [x] **Config-Driven Tool Registry**: `agent.json` controls `enabled_tools` array.
- [x] **Separation of Tenant Assets**: `tenants/<id>/assets/` separate from code.
- [x] **Single-Responsibility Services**: Decoupled `PromptBuilder`, `MemoryManager`, `ToolExecutor`, `AgentRunner`.
- [x] **Interface Abstractions**: Abstract classes for `VectorStore`, `StateStore`, and `NotificationProvider`.
- [x] **Domain-Generic Backend**: Backend engine only understands `Tenant`, `Conversation`, `Knowledge`, `Tool`, `Active Learning`, `Voice`.
- [x] **Self-Documenting Naming**: Explicit module and directory names throughout.
