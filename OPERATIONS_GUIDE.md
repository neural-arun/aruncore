# 🚀 ArunCore — Operations & Update Guide

Welcome to the **Master Operations & Maintenance Guide** for **ArunCore AI Assistant**.

This document covers everything: updating LinkedIn/GitHub data, re-indexing vector memory, deploying to all platforms, managing the Telegram Active Learning Loop, and CI/CD pipeline reference.

---

## 📋 Quick Command Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Sync LinkedIn Posts** | `python scripts/sync_linkedin.py` |
| **Sync GitHub Repositories** | `python scripts/sync_github_data.py` |
| **Re-index Vector Memory** | `python core/ingest.py` |
| **Run 30-Question Eval Suite** | `PYTHONPATH=. python scripts/evaluate_30_questions.py` |
| **Run Local Backend (FastAPI)** | `.venv/bin/uvicorn core.api:app --host 0.0.0.0 --port 8000 --reload` |
| **Run Local Frontend (Next.js)** | `cd frontend && npm run dev` |
| **Deploy EVERYTHING** | `git add . && git commit -m "update" && git push origin main` |

---

## 1. 💼 How to Update LinkedIn Data

When you publish new posts or career updates on LinkedIn:

### Step 1: Sync LinkedIn Posts
```bash
python scripts/sync_linkedin.py
```
Or manually edit [`data/static/public_profile.md`](data/static/public_profile.md) to add new achievements.

### Step 2: Re-Compile Vector Memory
```bash
python core/ingest.py
```
*(You will see: `Upsert complete. Ingestion sequence complete.`)*

### Step 3: Push to Production
```bash
git add . && git commit -m "data: update LinkedIn posts" && git push origin main
```
This automatically updates Vercel + Hugging Face via GitHub Actions.

---

## 2. 🐙 How to Update GitHub Project Data

When you create a new repo or update an existing project's `README.md`:

### Step 1: Run GitHub Sync Script
```bash
python scripts/sync_github_data.py
```
Fetches latest `README.md` and metadata from all public repos under `neural-arun`.

### Step 2: Re-Compile Vector Memory
```bash
python core/ingest.py
```

### Step 3: Push to Production
```bash
git add . && git commit -m "data: sync github projects" && git push origin main
```

---

## 3. 🧠 Telegram Active Learning Loop

This is the easiest way to teach the AI new things — **directly from your phone**.

### How It Works:
1. A user asks something unknown on the web chat or Telegram.
2. You receive an **instant alert** on Telegram (`@ai_twin_alert_bot`) with the question.
3. **Swipe right on the alert → Reply with your answer.**
4. The bot automatically:
   - Saves the Q&A pair to `data/raw/unknown_questions.json`
   - Re-ingests it into ChromaDB vector memory
   - Confirms: *"✅ Answer Saved & Ingested into AI Memory!"*
5. Next time anyone asks that question, the AI answers using your exact words.

### Manual Edit (if needed):
Edit `data/raw/unknown_questions.json` directly:
```json
[
  {
    "question": "What is your freelance rate?",
    "answer": "Project-based, starting at ₹50K for small scopes.",
    "timestamp": "2026-07-30T01:00:00Z"
  }
]
```
Then re-ingest:
```bash
python core/ingest.py
```

---

## 4. 🔁 Unknown Questions & Lead Capture Flow

When a visitor asks something the AI doesn't know:

1. **AI alerts Arun** on Telegram instantly via `@ai_twin_alert_bot`.
2. **AI asks the user** for their Name, Email or Phone/WhatsApp so Arun can follow up.
3. Arun **replies on Telegram** with the answer → AI learns it automatically (Section 3 above).

---

## 5. 🧪 How to Stress-Test & Evaluate Responses

To verify the AI answers accurately across 30 standard questions:
```bash
PYTHONPATH=. python scripts/evaluate_30_questions.py
```
Generates `test_output_30.json` with detailed answers, tools called, and response speeds.

---

## 6. 🔄 Automated CI/CD Pipeline — One Command to Rule Them All

```bash
git add . && git commit -m "your message" && git push origin main
```

| Platform | Trigger | What Happens | URL |
| :--- | :--- | :--- | :--- |
| **GitHub** | `git push` | Source code updated | [github.com/neural-arun/ArunCore](https://github.com/neural-arun/ArunCore) |
| **Vercel** | Auto GitHub webhook | Frontend rebuilt & deployed | [aruncore.vercel.app](https://aruncore.vercel.app) |
| **Hugging Face** | GitHub Actions (`.github/workflows/deploy.yml`) | Backend synced & redeployed | [huggingface.co/spaces/neural-arun/ArunCore](https://huggingface.co/spaces/neural-arun/ArunCore) |

### Required Secret (already set ✅):
- `HF_TOKEN` in [GitHub → Settings → Secrets → Actions](https://github.com/neural-arun/ArunCore/settings/secrets/actions)

---

## 7. 🔐 Environment Variables & Secrets Reference

### Local `.env` file:
```ini
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key

# Telegram Chat Log Bot (full execution trace logging)
TELEGRAM_BOT_TOKEN=your_log_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Telegram Lead Alert Bot (@ai_twin_alert_bot)
TELEGRAM_ALERT_BOT_TOKEN=your_alert_bot_token
TELEGRAM_ALERT_CHAT_ID=your_chat_id
```

### Hugging Face Space Secrets (Space Settings → Variables and Secrets):
| Secret Name | Purpose |
| :--- | :--- |
| `OPENAI_API_KEY` | LLM reasoning (`gpt-4.1-nano`) & Embeddings |
| `COHERE_API_KEY` | Vector search reranking (Cohere V3) |
| `TELEGRAM_BOT_TOKEN` | Chat history logging & full execution trace |
| `TELEGRAM_CHAT_ID` | Telegram log chat target ID |
| `TELEGRAM_ALERT_BOT_TOKEN` | Instant phone alerts (`@ai_twin_alert_bot`) |
| `TELEGRAM_ALERT_CHAT_ID` | Alert phone target ID |

### GitHub Repository Secrets (for CI/CD):
| Secret Name | Purpose |
| :--- | :--- |
| `HF_TOKEN` | Hugging Face Write Token for auto-deploy |

---

## 8. 📱 Mobile UI Notes

The chat UI is fully optimized for both mobile and desktop:
- **Mobile**: Full-width touch buttons, compact hero card, 2-line prompt cards, sticky STT input container.
- **Desktop/Laptop**: Layout completely unchanged from original design.

---

## 9. 🗣️ Language Behavior

- **English queries** → 100% clean, professional English. No Hindi slang.
- **Hindi / Hinglish queries** → Natural, witty Hinglish.
- Tone and persona remain consistent. Only the language adapts.
