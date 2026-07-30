---
title: ArunCore AI Assistant
emoji: 🧠
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
pinned: false
---

# 🧠 Arun Yadav — AI Systems Architect & Personal AI Assistant

**ArunCore** is a production-grade, stateful, agentic portfolio and personal AI assistant built for **Arun Yadav** (AI Systems Architect specializing in Healthcare & Education). 

It features an intelligent conversational assistant equipped with real-time NDJSON token streaming, OpenAI Studio Neural Speech (TTS), Web Speech Voice-to-Text (STT), zero-hallucination hybrid RAG, live GitHub data inspection, and a dual-bot Telegram lead handoff system.

---

## 🌟 Key Features

1. **🤖 Arun's AI Assistant Persona**:
   - Witty, casual, straightforward, and cool-friend vibe with zero corporate fluff.
   - **Dynamic Language Matching**: Responds in clean, articulate English for international/corporate queries, and natural Hinglish/Hindi whenever visitors chat in Hindi.

2. **🎙️ Voice Studio (HD Neural TTS & STT)**:
   - **Text-to-Speech (TTS)**: Built-in `[ 🔊 Listen (HD Voice) ]` button powered by OpenAI's `tts-1` studio neural voice (`/tts` endpoint) with automatic browser Web Speech fallback.
   - **Speech-to-Text (STT)**: Built-in Microphone `[ 🎙️ ]` button in the text input container allowing users to speak directly into the chat input with real-time transcription.

3. **⚡ Real-Time Token Streaming**:
   - Streaming NDJSON response buffer over HTTP with a live radar pulse status indicator, typing cursor (`▌`), and collapsible step-by-step engine execution trace drawer.

4. **🚨 Proactive Lead Capture & Dual Telegram Bots**:
   - When visitors ask about hiring Arun or submitting project inquiries, the assistant provides direct contact details (+91 8881109193, `neural.arun.dev@gmail.com`), prompts for the lead's contact details, and triggers an instant Telegram alert to Arun's phone.
   - **Dual Bot Separation**:
     - `TELEGRAM_ALERT_BOT_TOKEN` (`@ai_twin_alert_bot`): Instant phone alerts for leads & urgent contact queries.
     - `TELEGRAM_BOT_TOKEN`: Background transcript logging and system debug event traces.

5. **🔍 Zero-Hallucination Hybrid RAG & Live GitHub Engine**:
   - Combines dense vector embeddings (**ChromaDB**), BM25 keyword search, and **Cohere V3 Reranker** for grounded answers.
   - Live GitHub tool (`get_github_live_data`) to fetch real-time repositories, commits, and project activity on demand.

6. **🎨 Modern Light-Default UI**:
   - Built with **Next.js 16 (Turbopack)**, Tailwind CSS, Lucide icons, and React Markdown.
   - Symmetrical 100% single-viewport landing page with Hero profile card, 2x2 interactive question grid, and prominent input container.

---

## 🏗️ System Architecture

```
.
├── core/                  # Python FastAPI & LangChain Agent Backend
│   ├── agent.py           # Core agent loop, persona rules, RAG tools & dual Telegram handlers
│   ├── api.py             # FastAPI streaming server (NDJSON /chat) & OpenAI HD Neural Voice (/tts)
│   ├── ingest.py          # Vector database indexing pipeline
│   └── bot.py             # Public Telegram bot service
├── frontend/              # Next.js 16 Web Application
│   ├── app/               # Next.js App Router (page.tsx, layout.tsx, globals.css)
│   ├── components/        # React components (Header, ChatPanel, ManifestoView, ProjectsView)
│   └── lib/               # Types & API client helpers
├── data/                  # Single source of truth knowledge base
│   ├── static/            # public_profile.md (identity/skills) & rules_of_engagement.md
│   └── github/            # Curated markdown document repositories
├── scripts/               # Automation scripts
│   ├── sync_github_data.py # Auto-syncs GitHub repos & READMEs
│   └── sync_linkedin.py   # Apify LinkedIn post sync script
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Environment Setup
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TELEGRAM_ALERT_BOT_TOKEN=your_telegram_alert_bot_token
TELEGRAM_ALERT_CHAT_ID=your_telegram_chat_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Backend Launch (FastAPI)
```bash
# Activate virtual environment
source .venv/bin/activate

# Ingest knowledge base into ChromaDB
python core/ingest.py

# Start FastAPI Uvicorn Server
uvicorn core.api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Launch (Next.js 16)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000 in your browser
```

---

## 🛠️ Tech Stack

- **Core & AI Backend**: Python 3.11, FastAPI, Uvicorn, LangChain, OpenAI (GPT-4o-mini & TTS-1), ChromaDB, BM25, Cohere Reranker.
- **Frontend & UI**: Next.js 16 (Turbopack), React 19, TypeScript, Tailwind CSS, Lucide Icons, Web Speech API.
- **Notifications & Integrations**: Telegram Bot API, GitHub REST API.

---

*Built by Arun Yadav — AI Systems Architect specializing in Healthcare & Education.*  
*Contact: +91 8881109193 | neural.arun.dev@gmail.com*
