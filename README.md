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

It features an intelligent conversational assistant equipped with `gpt-4.1-nano`, real-time NDJSON token streaming, OpenAI Studio Neural Speech (TTS), Web Speech Voice-to-Text (STT), zero-hallucination hybrid RAG, live GitHub data inspection, value-first project inquiry logic, a dual-bot Telegram lead handoff system, a **Telegram Active Learning Loop**, and **fully automated CI/CD deployment** via GitHub Actions.

---

## 🌟 Key Features

1. **🤖 Arun's AI Assistant Persona**:
   - Witty, casual, straightforward, and cool-friend vibe with zero corporate fluff.
   - **Strict Dynamic Language Matching**: Responds in 100% clean, articulate English for English queries. Responds naturally in Hinglish/Hindi when the user speaks Hindi. No mixing.

2. **💡 Value & Problem-Solving First Project Inquiries**:
   - When asked about projects, the AI leads with **real-world business value, problem-solving impact, and time/cost savings** before detailing technical architecture.
   - **Smart Alias Search**: Project name variations (e.g. "MedCoach", "med coach", "clinical tutor") are intelligently resolved to the correct repository README.

3. **🎙️ Voice Studio (HD Neural TTS & STT)**:
   - **Text-to-Speech (TTS)**: `[ 🔊 Listen (HD Voice) ]` button powered by OpenAI's `tts-1` studio neural voice (`/tts` endpoint) with Web Speech fallback.
   - **Speech-to-Text (STT)**: `[ 🎙️ ]` microphone button with **duplicate-free transcription** (fixed interim result compounding bug).

4. **⚡ Real-Time Token Streaming**:
   - NDJSON streaming over HTTP with a live radar pulse status indicator, typing cursor (`▌`), and collapsible step-by-step engine execution trace drawer.

5. **🚨 Proactive Lead Capture & Dual Telegram Bots**:
   - **Unknown Questions**: When a user asks something the AI doesn't know, it **alerts Arun instantly** on Telegram AND asks the user for their **Name, Email or Phone** so Arun can follow up directly.
   - **Hiring/Contact Queries**: Provides Arun's direct contact details (+91 8881109193, `neural.arun.dev@gmail.com`) and triggers an instant phone alert.
   - **Dual Bot Separation**:
     - `TELEGRAM_ALERT_BOT_TOKEN` (`@ai_twin_alert_bot`): Instant phone alerts for leads & urgent queries.
     - `TELEGRAM_BOT_TOKEN`: Background transcript logging with full execution trace (tools called, retrieved chunks, steps).

6. **🧠 Telegram Active Learning Loop**:
   - When Arun **replies to an UNKNOWN_QUESTION alert** on Telegram, the bot automatically:
     - Saves the Q&A pair to `data/raw/unknown_questions.json`.
     - Re-ingests into ChromaDB vector memory in the background.
     - Confirms with: *"✅ Answer Saved & Ingested into AI Memory!"*
   - Next time any user asks that question (web or Telegram), the AI answers using Arun's exact words.

7. **🔍 Zero-Hallucination Hybrid RAG & Live GitHub Engine**:
   - Alias-aware project search (resolves `MedCoach` → `med_coach/README.md`).
   - Always checks `data/raw/unknown_questions.json` for Arun's verified human answers.
   - Combines ChromaDB dense embeddings, BM25 keyword search, and Cohere V3 Reranker.

8. **📱 Mobile-Optimized UI**:
   - Full-width touch-friendly buttons, compact hero card layout, correct touch target sizes — desktop layout completely unchanged.

9. **🔄 Fully Automated CI/CD Pipeline**:
   - One command: `git push origin main` → **GitHub + Vercel + Hugging Face** all update automatically.

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
│ + unknown   │        └─────────────┘      │ + Active    │
│ _questions  │                             │ Learning    │
└─────────────┘                             └─────────────┘

┌─────────────────────────────────────────────────────────┐
│                 GitHub Actions CI/CD                    │
│  git push → GitHub → Vercel (auto) + HF Space (auto)   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure Overview

- [core/README.md](core/README.md): FastAPI backend, agent loop (`gpt-4.1-nano`), vector store compiler, and endpoints.
- [frontend/README.md](frontend/README.md): Next.js 16 UI components, voice studio controls, and static export setup.
- [data/README.md](data/README.md): Knowledge base files including `unknown_questions.json` active learning store.
- [scripts/README.md](scripts/README.md): Data sync scripts (GitHub & LinkedIn) and 30-question evaluation suite.
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md): Master operational guide — how to update data, push to all platforms, and manage the active learning loop.
- [.github/workflows/deploy.yml](.github/workflows/deploy.yml): GitHub Actions workflow for automated Hugging Face deployment on every push.

---

## 🔄 CI/CD Deployment (Automated)

```bash
# This single command updates EVERYTHING:
git add . && git commit -m "your update" && git push origin main
```

| Platform | Trigger | URL |
|---|---|---|
| **GitHub** | `git push` | [github.com/neural-arun/ArunCore](https://github.com/neural-arun/ArunCore) |
| **Vercel** | Auto via GitHub webhook | [aruncore.vercel.app](https://aruncore.vercel.app) |
| **Hugging Face** | Auto via GitHub Actions | [huggingface.co/spaces/neural-arun/ArunCore](https://huggingface.co/spaces/neural-arun/ArunCore) |

---

## 🔐 Environment Variables (`.env`)

```ini
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key

# Telegram Chat Log Bot (full trace logging)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Telegram Lead Alert Bot (@ai_twin_alert_bot)
TELEGRAM_ALERT_BOT_TOKEN=your_alert_bot_token
TELEGRAM_ALERT_CHAT_ID=your_chat_id
```

**GitHub Repository Secret** (for CI/CD auto-deploy to Hugging Face):
- `HF_TOKEN` = Your Hugging Face Write Access Token (set in GitHub → Settings → Secrets → Actions)
