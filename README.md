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

It features an intelligent conversational assistant equipped with `gpt-4.1-nano`, real-time NDJSON token streaming, OpenAI Studio Neural Speech (TTS), Web Speech Voice-to-Text (STT), zero-hallucination hybrid RAG, live GitHub API data sync, value-first project inquiry logic, **100% automated Telegram notifications**, a **1-Click Magic Link 3-Way Real Human Takeover Engine**, a **Telegram Active Learning Loop**, and **fully automated CI/CD deployment** via GitHub Actions.

---

## 🌟 Key Features

1. **🤖 Arun's AI Assistant Persona**:
   - Witty, casual, straightforward, and cool-friend vibe with zero corporate fluff.
   - **Strict Exact Language Matching**: Responds in 100% clean, articulate English for English queries with zero Hindi/Hinglish slang leaks. Responds naturally in Hinglish/Hindi when the user speaks Hindi.

2. **⚡ 100% Automated Telegram Alerts (Zero LLM Dependency)**:
   - **Every Single Visitor Message**: Automatically triggers an instant notification to Arun's Telegram Alert Bot without depending on LLM decision gates or category filters.
   - Includes: User Question, AI Twin Response, Session ID, and a **1-Click Magic Join Link**.

3. **👨‍💻 1-Click Magic Link 3-Way Real Human Takeover**:
   - **Seamless Intervention**: Clicking `https://aruncore.vercel.app/?session_id=...&admin_token=...` in Telegram opens the website directly in **Admin Mode** on any device.
   - **Admin Reply Bar**: Unlocks a dedicated input box allowing Arun to post messages live as `👨‍💻 Arun Yadav [VERIFIED HUMAN] 🟢`.
   - **3-Way Conversation**: The AI Twin continues answering visitor questions instantly, while Arun can chime in alongside the AI in real time.

4. **🌐 Vercel Serverless Telegram Egress Relay**:
   - Next.js `/api/telegram` serverless endpoint routes all outbound Telegram API traffic through Vercel serverless functions, bypassing Hugging Face Space egress firewall restrictions on Telegram IP ranges.

5. **🧠 Telegram Active Learning Loop**:
   - When Arun **replies to an alert message** on Telegram, the bot automatically:
     - Extracts the question and saves the verified answer to `data/raw/unknown_questions.json`.
     - Re-ingests into ChromaDB vector memory in the background.
     - Confirms with: *"✅ Answer Saved & Ingested into AI Memory!"*

6. **💡 Value & Problem-Solving First Project Inquiries**:
   - Leads with **real-world business value, problem-solving impact, and high-friction operational workflows** (time, accuracy, human energy) before detailing technical architecture.
   - **Smart Alias Search**: Intelligently maps variations like "MedCoach" to the correct repository README.

7. **🐙 Live GitHub API Auto-Sync**:
   - Real-time client-side sync fetching repositories live from `api.github.com/users/neural-arun/repos`.
   - Automatically sorted by `pushed_at` descending with live commit pulse indicators.

8. **🎙️ Voice Studio (HD Neural TTS & STT)**:
   - **Text-to-Speech (TTS)**: OpenAI `tts-1` studio neural voice (`/tts` endpoint) with Web Speech fallback.
   - **Speech-to-Text (STT)**: Microphone button with duplicate-free transcription.

9. **📱 Mobile-Optimized UI**:
   - Full-width touch-friendly controls, responsive hero card layout, compact status indicators, and dark/light mode toggle.

10. **🔄 Fully Automated CI/CD Pipeline**:
    - One command: `git push origin main` → **GitHub + Vercel + Hugging Face** all update automatically.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Interface                     │
│  Next.js 16 • 3-Way Live Chat • 1-Click Magic Link Admin│
└────────────────────────────┬────────────────────────────┘
                             │ HTTP POST /chat & /tts
┌────────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                      │
│             (port 8000 / HF Docker port 7860)           │
└──────┬──────────────────────┬────────────────────┬──────┘
       │                      │                    │
┌──────▼──────┐        ┌──────▼──────┐      ┌──────▼──────┐
│ ChromaDB +  │        │ Live GitHub │      │ Vercel Relay│
│ Cohere V3   │        │     API     │      │ Telegram    │
│ + unknown   │        └─────────────┘      │ Alerts +    │
│ _questions  │                             │ 3-Way Chat  │
└─────────────┘                             └─────────────┘

┌─────────────────────────────────────────────────────────┐
│                 GitHub Actions CI/CD                    │
│  git push → GitHub → Vercel (auto) + HF Space (auto)   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure Overview

- [core/README.md](core/README.md): FastAPI backend, agent loop (`gpt-4.1-nano`), 3-way human takeover endpoints, vector store compiler.
- [frontend/README.md](frontend/README.md): Next.js 16 UI components, Vercel Telegram relay route (`/api/telegram`), admin mode controls.
- [data/README.md](data/README.md): Knowledge base files including `unknown_questions.json` active learning store.
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md): Master operational guide — how to manage data, use live takeover links, and run system tests.

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

# Telegram Chat Log Bot (full execution trace logging)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Telegram Alert Bot (@ai_twin_alert_bot)
TELEGRAM_ALERT_BOT_TOKEN=your_alert_bot_token
TELEGRAM_ALERT_CHAT_ID=your_chat_id

# Admin Takeover Secret Key
ADMIN_SECRET_KEY=your_admin_secret_key
```

**GitHub Repository Secret** (for CI/CD auto-deploy to Hugging Face):
- `HF_TOKEN` = Your Hugging Face Write Access Token
