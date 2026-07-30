---
title: ArunCore AI Assistant
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 🧠 Arun Yadav — AI Systems Architect & Personal AI Assistant

**ArunCore** is a production-grade, stateful, agentic portfolio and personal AI assistant built for **Arun Yadav** (AI Systems Architect specializing in Healthcare & Education). 

It features an intelligent conversational assistant equipped with `gpt-4.1-nano`, real-time NDJSON token streaming, OpenAI Studio Neural Speech (TTS), Web Speech Voice-to-Text (STT), zero-hallucination hybrid RAG, live GitHub data inspection, value-first project inquiry logic, and a dual-bot Telegram lead handoff system.

---

## 🌟 Key Features

1. **🤖 Arun's AI Assistant Persona**:
   - Witty, casual, straightforward, and cool-friend vibe with zero corporate fluff.
   - **Dynamic Language Matching**: Responds in clean, articulate English for international/corporate queries, and natural Hinglish/Hindi whenever visitors chat in Hindi.

2. **💡 Value & Problem-Solving First Project Inquiries**:
   - When asked about projects, the AI leads with **real-world business value, problem-solving impact, and time/cost savings** before detailing technical architecture.

3. **🎙️ Voice Studio (HD Neural TTS & STT)**:
   - **Text-to-Speech (TTS)**: Built-in `[ 🔊 Listen (HD Voice) ]` button powered by OpenAI's `tts-1` studio neural voice (`/tts` endpoint) with automatic browser Web Speech fallback.
   - **Speech-to-Text (STT)**: Built-in Microphone `[ 🎙️ ]` button in the text input container allowing users to speak directly into the chat input with real-time transcription.

4. **⚡ Real-Time Token Streaming**:
   - Streaming NDJSON response buffer over HTTP with a live radar pulse status indicator, typing cursor (`▌`), and collapsible step-by-step engine execution trace drawer.

5. **🚨 Proactive Lead Capture & Dual Telegram Bots**:
   - When visitors ask about hiring Arun or submitting project inquiries, the assistant provides direct contact details (+91 8881109193, `neural.arun.dev@gmail.com`), prompts for the lead's contact details, and triggers an instant Telegram alert to Arun's phone.
   - **Dual Bot Separation**:
     - `TELEGRAM_ALERT_BOT_TOKEN` (`@ai_twin_alert_bot`): Instant phone alerts for leads & urgent contact queries.
     - `TELEGRAM_BOT_TOKEN`: Background transcript logging and system debug event traces.

6. **🔍 Zero-Hallucination Hybrid RAG & Live GitHub Engine**:
   - Combines dense vector embeddings (**ChromaDB**), BM25 keyword search, and **Cohere V3 Reranker** for grounded answers.
   - Live GitHub tool (`get_github_live_data`) to fetch real-time repositories, commits, and project activity on demand.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Interface                     │
│    Next.js 16 • Tailwind CSS • HD Voice & STT Studio    │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP POST /chat & /tts
┌────────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                      │
│             (port 8000 / HF Docker port 7860)           │
└──────┬──────────────────────┬────────────────────┬──────┘
       │                      │                    │
┌──────▼──────┐        ┌──────▼──────┐      ┌──────▼──────┐
│ ChromaDB +  │        │ Live GitHub │      │ Dual-Bot    │
│ Cohere V3   │        │     API     │      │ Telegram    │
└─────────────┘        └─────────────┘      └─────────────┘
```

---

## 📁 Repository Structure Overview

- [core/README.md](file:///home/arun/projects/profile/core/README.md): FastAPI backend, agent loop (`gpt-4.1-nano`), vector store compiler, and endpoints.
- [frontend/README.md](file:///home/arun/projects/profile/frontend/README.md): Next.js 16 UI components, voice studio controls, and static export setup.
- [data/README.md](file:///home/arun/projects/profile/data/README.md): Knowledge base files (`public_profile.md`, `rules_of_engagement.md`, project markdown files).
- [scripts/README.md](file:///home/arun/projects/profile/scripts/README.md): Data sync scripts (GitHub & LinkedIn) and 30-question evaluation suite.
- [OPERATIONS_GUIDE.md](file:///home/arun/projects/profile/OPERATIONS_GUIDE.md): Master operational guide for pushing updates, syncing data, and managing deployments.

---

## 🔐 Environment Variables (`.env`)

```ini
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key

# Telegram Chat Log Bot
TELEGRAM_BOT_TOKEN=8678897707:AAGir63LUcbL-w9TILmkoPSxHgBXfhC8on4
TELEGRAM_CHAT_ID=1154451605

# Telegram Lead Alert Bot (@ai_twin_alert_bot)
TELEGRAM_ALERT_BOT_TOKEN=8847600936:AAGHCH1bBVMGSXl_MSrxo1klwgrUGJyeDW0
TELEGRAM_ALERT_CHAT_ID=1154451605
```
