---
title: ArunCore Enterprise AI Platform & Digital Twin System
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 🧠 ArunCore — Domain-Generic Multi-Tenant Enterprise AI Platform & Digital Twin

> **Architecture Spec Version:** ❄️ **v1.0 FROZEN**  
> **Engine:** `gpt-4.1-nano` | **RAG:** ChromaDB (Dense) + BM25 (Sparse) + Cohere V3 (Reranker)  
> **Frontend:** Next.js 16 (App Router) Luxury Dark/Light UI  
> **Backend:** FastAPI Decoupled Microservices  
> **Evaluation:** Automated 30-Question Multi-Turn ReAct Stress-Test Suite

---

## 🎯 Platform Overview

**ArunCore** is a domain-generic, multi-tenant enterprise AI platform and stateful personal digital twin built for **Arun Yadav** (AI Systems Architect specializing in Healthcare & Education).

The platform serves dual core functions:
1. **Personal AI Digital Twin**: A 24/7 interactive representative of Arun Yadav, providing deep technical answers about his AI architectures, healthcare/education projects, GitHub repositories, and LinkedIn publications, backed by instant lead capture and dual Telegram alert capabilities.
2. **Multi-Tenant Enterprise JSON Engine (`?tutor=<tutor_id>`)**: A zero-code multi-tenant advisor system capable of instantly spinning up bespoke 24/7 AI Course Advisors and Sales Representatives for any client or instructor (e.g. Ed Donner) via a single 238-key enterprise JSON schema dictionary.

---

## 🏛️ Core Architecture Principles (Golden Rules)

1. **Preserve Frontend 100%**: Next.js luxury UI (`app/page.tsx`, `ChatPanel.tsx`, `ProjectsView.tsx`, `ManifestoView.tsx`, `Header.tsx`) with glowing accent borders, light/dark themes, hero card, and tab views stays 100% intact.
2. **Zero Functionality Loss**: Retains Hybrid RAG, active Telegram alerts, 3-way live human chat takeover, TTS neural voice studio, and evaluation harness.
3. **Production-Grade Hybrid RAG Engine**: ChromaDB dense vector search + BM25 sparse keyword search + Cohere English V3 reranking for high-precision, zero-hallucination retrieval.
4. **Dynamic JSON Config Engine**: Zero hardcoded `if client == "ed"` logic in Python or TypeScript. 100% of tenant branding, prompts, tools, headers, and catalogs resolve dynamically from JSON dictionaries (`demos/<tutor_id>_enterprise_dictionary.json`).
5. **Config-Driven Tool Registry**: Client tools are controlled via `enabled_tools` array in config (`["search_arun_knowledge", "get_github_live_data", "notify_arun"]`).
6. **Decoupled Backend Services**: Monoliths are banned; small single-responsibility services (`PromptBuilder`, `MemoryManager`, `ToolExecutor`, `RAGService`, `TenantService`, `VoiceService`, `ActiveLearningService`).

---

## ⚡ Key Technical Capabilities

### 1. 🤖 7-Iteration Recursive Agentic Loop (`gpt-4.1-nano`)
- Powered by `gpt-4.1-nano` with up to **7 recursive tool execution turns** (`search_arun_knowledge`, `get_github_live_data`, `notify_arun`) per turn.
- Executes multi-step technical comparisons, live GitHub commit fetches, and knowledge base retrievals before generating answers.

### 2. 📚 2-Step GitHub & Knowledge Base Retrieval Pipeline
- Automatically fetches the 3 most recently updated repositories and live commit logs from GitHub API (`get_github_live_data`).
- Automatically queries local README architectures (`search_arun_knowledge`) for each returned repository name to provide deep technical details and direct clickable URLs.

### 3. 📊 Markdown Table & Direct Project Link Mandate
- Presents all multi-system comparisons (e.g. MedCoach vs NEET Bot vs Legal RAG) in clean **Markdown Tables**.
- Embeds direct, clickable GitHub URLs (`https://github.com/neural-arun/<repo>`) directly inside table headers and project descriptions.

### 4. 💼 LinkedIn Insights & Social Engagement CTA
- Integrates scraped public LinkedIn posts (`data/linkedin/posts.md`) covering AI workforce trends (2026–2036), NEET CBT practice ecosystem, FastAPI Todo API, and BPSC Rank 5 updates.
- Appends direct clickable LinkedIn post URLs and natural social engagement calls-to-action inviting visitors to like, comment, or share their thoughts.

### 5. 🚨 Dual-Channel Telegram Alerts & 3-Way Live Human Chat Takeover
- **Active Learning Logger**: Silently logs all chats to `@ai_twin_alert_bot`.
- **Urgent Lead Alert Bot**: Instantly alerts Arun's phone for hiring leads, unknown questions, or urgent inquiries with a **1-Click Magic Join Link** for real-time 3-way human chat takeover.

---

## 📁 Repository Directory Map

```text
profile/
├── backend/                  # Python FastAPI Backend Architecture
│   └── app/
│       ├── api/v1/           # API Endpoints (/config, /chat, /voice, /webhook)
│       ├── core/             # Core Orchestration (agent.py, api.py, bot.py, ingest.py)
│       ├── schemas/          # Pydantic Schemas (tenant.py, chat.py, voice.py)
│       ├── services/         # Decoupled Business Logic Services
│       └── main.py           # FastAPI Application Entrypoint
├── frontend/                 # Next.js 16 (App Router) Luxury UI
│   ├── app/                  # Page Routes & Global Styles
│   ├── components/           # UI Components (ChatPanel, Header, ProjectsView, etc.)
│   └── public/               # Static Avatars & Logos
├── data/                     # Data Stores & Knowledge Assets (Excluded from Git code bloat)
│   ├── github/               # Readme files for all 21 public GitHub repos
│   ├── linkedin/             # Scraped LinkedIn posts (posts.md)
│   ├── raw/                  # Personal background & unknown questions DB
│   └── static/               # Public profile, rules of engagement, voice persona
├── db/                       # ChromaDB Vector Database & Ingestion State
├── demos/                    # Enterprise 238-Key Monolithic JSON Schemas
│   ├── ed_donner_enterprise_dictionary.json
│   ├── general.json          # Master 238-key JSON Template
│   └── master_enterprise_dictionary.json
├── scripts/                  # Automated Maintenance & Evaluation Suite
│   ├── evaluate.py           # 30-Question Multi-Turn ReAct Test Harness
│   ├── evaluation_questions.md # 30 Test Questions List
│   ├── evaluation_results.md  # Generated Output & Execution Traces
│   ├── ingest.py             # ChromaDB Re-Ingestion Script
│   ├── sync_github.py        # GitHub API Auto-Sync Script
│   ├── sync_linkedin.py      # LinkedIn Posts Sync Script
│   └── sync_all.py           # 1-Click Master Data Sync Runner
├── tenants/                  # Multi-Tenant 6-File JSON Configurations
├── tests/                    # Automated Unit & Integration Test Suite
├── AGENTS.md                 # Master Protocol & Execution Rules for AI Coding Agents
└── aruncore_master_blueprint.md # Complete Architecture Specification Doc
```

---

## 🚀 Quick Start & Local Execution

### 1. Environment Setup
Ensure `.env` exists in root with valid API keys:
```env
OPENAI_API_KEY=sk-proj-...
COHERE_API_KEY=...
GITHUB_USERNAME=neural-arun
GITHUB_TOKEN=github_pat_...
```

### 2. Run Backend Server (FastAPI on Port 8000)
```bash
source .venv/bin/activate
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Run Frontend Dev Server (Next.js on Port 3000)
```bash
cd frontend
npm run dev
```

### 4. Run Automated Evaluation Test Suite
```bash
python3 scripts/evaluate.py
```

---

## 🧪 Verification & Automated Testing

Execute the complete backend unit test suite:
```bash
python3 -m unittest discover -s tests
```
*Expected Output:* `Ran 9 tests in 0.028s OK`

---

## 📜 License & Copyright

© 2026 **Arun Yadav** ([neural.arun.dev@gmail.com](mailto:neural.arun.dev@gmail.com)). All rights reserved.
