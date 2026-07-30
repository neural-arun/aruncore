# 🚀 ArunCore Operations & Update Guide

Welcome to the **Master Operations & Maintenance Guide** for **ArunCore AI Assistant**. 

This document explains step-by-step how to update your LinkedIn data, sync fresh GitHub projects, re-index vector database memory, and push updates to **GitHub**, **Hugging Face Spaces**, and **Vercel**.

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
| **Push Code to GitHub** | `git add . && git commit -m "update" && git push origin main` |

---

## 1. 💼 How to Update & Re-Sync LinkedIn Data

When you publish new posts, articles, or career updates on LinkedIn, follow these steps to make your AI assistant aware of them:

### Step 1: Add or Sync LinkedIn Posts
- If you use Apify automated sync, run:
  ```bash
  python scripts/sync_linkedin.py
  ```
- Or edit [data/static/public_profile.md](file:///home/arun/projects/profile/data/static/public_profile.md) directly to add major achievements or post summaries under `# Social Insights & LinkedIn Posts`.

### Step 2: Re-Compile Vector DB Memory
After modifying any markdown file in `data/`, compile the new embeddings into ChromaDB:
```bash
python core/ingest.py
```
*(You will see `Upsert complete. Ingestion sequence complete.`)*

### Step 3: Push to Production
Push the updated knowledge base to GitHub and Hugging Face (see Section 4 & 5).

---

## 2. 🐙 How to Update & Re-Sync GitHub Project Data

When you create a new GitHub repository or update a project's `README.md`:

### Step 1: Run the GitHub Data Sync Script
```bash
python scripts/sync_github_data.py
```
This fetches the latest `README.md` and metadata from all public repositories under `neural-arun` and writes them into `data/github/`.

### Step 2: Re-Compile Vector DB Memory
```bash
python core/ingest.py
```

### Step 3: Push to Production
Push the updated project files to GitHub and Hugging Face (see Section 4 & 5).

---

## 3. 🧪 How to Stress-Test & Evaluate Responses

To verify that your AI Assistant responds accurately with your witty persona and zero hallucinations across 30 standard questions:

```bash
PYTHONPATH=. python scripts/evaluate_30_questions.py
```

This generates `test_output_30.json` containing detailed answers, tools called, and response speeds.

---

## 4. 🐙 How to Push Updates to GitHub

Whenever you edit code or data files locally, push your changes to GitHub:

```bash
git add .
git commit -m "feat: add new LinkedIn post and update knowledge base"
git push origin main
```

*(Repository URL: `https://github.com/neural-arun/ArunCore`)*

---

## 5. 🤗 How to Deploy Updates to Hugging Face Spaces

Hugging Face Spaces (`neural-arun/ArunCore`) runs your app in a Docker container on port `7860`.

Because Hugging Face rejects large binary files (like local SQLite databases), we use an **orphan deployment branch** script to push source code cleanly:

### Deployment Commands (Run from Project Root):

```bash
# 1. Ensure your local main branch is committed
git add . && git commit -m "production update" || true

# 2. Push orphan deployment branch to Hugging Face
git checkout --orphan hf-deploy-v13
git rm -rf --cached Images/ db/ *.png 2>/dev/null || true
git rm --cached frontend/public/logo.jpg frontend/public/next.svg frontend/public/vercel.svg 2>/dev/null || true
git commit -m "deploy: update Hugging Face Space"
git push --force https://neural-arun:hf_your_huggingface_access_token@huggingface.co/spaces/neural-arun/ArunCore hf-deploy-v13:main

# 3. Switch back to your working main branch
git checkout -f main
```

👉 **Live Hugging Face Space URL**: [`https://huggingface.co/spaces/neural-arun/ArunCore`](https://huggingface.co/spaces/neural-arun/ArunCore)

---

## 6. 🌐 How to Deploy Frontend Updates to Vercel

If you host the Next.js UI on Vercel ([aruncore.vercel.app](https://aruncore.vercel.app)):

### Automatic Deployment:
Every time you run `git push origin main` (Section 4), Vercel automatically detects the push and rebuilds the site!

### Requirements in Vercel Settings:
1. **Root Directory**: Must be set to `frontend` under **Vercel Project Settings > General**.
2. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL` = `https://neural-arun-aruncore.hf.space` *(or your local API backend)*.

---

## 🔑 Environment Variables & Secrets Reference

When setting up a new environment or deploying on Hugging Face Spaces (**Space Settings > Variables and Secrets**), enter these keys:

| Secret Name | Purpose | Value Example |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | LLM reasoning (`gpt-4.1-nano`) & Embeddings | `sk-proj-...` |
| `COHERE_API_KEY` | Vector search reranking (Cohere V3) | `your_cohere_key` |
| `TELEGRAM_BOT_TOKEN` | Chat history logging & debug traces | `8678897707:AAGir63LUcbL-w9TILmkoPSxHgBXfhC8on4` |
| `TELEGRAM_CHAT_ID` | Telegram chat target ID | `1154451605` |
| `TELEGRAM_ALERT_BOT_TOKEN` | Instant phone alerts for hiring leads (`@ai_twin_alert_bot`) | `8847600936:AAGHCH1bBVMGSXl_MSrxo1klwgrUGJyeDW0` |
| `TELEGRAM_ALERT_CHAT_ID` | Alert phone target ID | `1154451605` |

---

## 7. Automated Multi-Platform CI/CD Pipeline

Whenever you push code updates to `git push origin main`:
1. **GitHub Repository**: Receives latest source code and documentation updates.
2. **GitHub Actions Workflow**: Automatically triggers `.github/workflows/deploy.yml` using your `HF_TOKEN` secret to push and deploy directly to Hugging Face Spaces.
3. **Vercel Production**: Automatically builds and deploys the Next.js frontend from the GitHub webhook!
