# 📊 Knowledge Base Data Directory (`/data/`)

This folder is the **single source of truth knowledge base** for Arun's AI Assistant. The ingestion engine (`core/ingest.py`) indexes all files here into ChromaDB vector memory.

---

## 📁 Directory Structure

```
data/
├── static/
│   ├── public_profile.md         # Core identity, contact info, project value specs, stack & career overview
│   └── rules_of_engagement.md   # Behavioral rules, safety boundaries, and response guidelines
├── github/                       # 22+ curated project repositories (README + metadata per repo)
│   └── [project_name]/
│       ├── README.md             # Full project README scraped from GitHub
│       └── metadata.json         # Stars, language, last push, topics
├── linkedin/
│   └── profile_summary.md        # Synced LinkedIn posts, insights, and engagement metrics
└── raw/
    └── unknown_questions.json    # ← Active Learning Store: Arun's Telegram-verified Q&A pairs
```

---

## 📁 Detailed File Overview

### 1. `data/static/public_profile.md`
- Defines Arun Yadav's background, contact details (+91 8881109193, `neural.arun.dev@gmail.com`), core engineering philosophy, specialization in Healthcare & Education AI systems, detailed project specs (Legal RAG IPC chunking, MedCoach reasoning tutor, NEET 10,000+ MCQs, 99acres scraper), and LinkedIn insights.

### 2. `data/static/rules_of_engagement.md`
- Defines strict system instructions for the AI assistant — zero hallucination rules, when to cite GitHub repos, how to handle unknown questions, when to trigger lead alerts, and language matching behavior.

### 3. `data/github/` — Project Knowledge Base
- Contains 22+ individual subfolders for each of Arun's projects (e.g., `ArunCore`, `deep_research`, `legal_RAG_system`, `med_coach`, `neet-bot`). Each folder contains a detailed `README.md` and `metadata.json` for RAG vector retrieval.
- **Alias Resolution**: The search engine maps common name variations (e.g. `MedCoach`, `med coach`, `clinical tutor`) to the correct project folder automatically.

### 4. `data/linkedin/profile_summary.md`
- Contains synced LinkedIn posts and articles written by Arun, allowing the AI assistant to reference his public technical thoughts and insights.

### 5. `data/raw/unknown_questions.json` ← 🆕 Active Learning Store
- **What it is**: A JSON file that stores Q&A pairs verified by Arun himself via Telegram.
- **How it works**:
  1. A user asks something the AI can't answer → AI flags it as UNKNOWN and alerts Arun on Telegram.
  2. Arun **replies to that Telegram alert** with the correct answer.
  3. The bot auto-saves the pair here and re-ingests it into ChromaDB.
  4. Next time anyone asks that question (web or Telegram), the AI answers using Arun's exact words.
- **Format**:
  ```json
  [
    {
      "question": "What is your freelance rate?",
      "answer": "My project-based rate starts at ₹50K for small scopes.",
      "timestamp": "2026-07-30T01:05:00Z"
    }
  ]
  ```

---

## ➕ How to Add New Knowledge

### Option A: Edit Markdown Directly
Edit `data/static/public_profile.md`, then run:
```bash
python core/ingest.py
```

### Option B: Sync Fresh GitHub Projects
```bash
python scripts/sync_github_data.py
python core/ingest.py
```

### Option C: Telegram Active Learning (Easiest — Mobile!)
1. Someone asks an unknown question on web/Telegram.
2. You get a Telegram alert on your phone.
3. **Swipe reply → type your answer → send**.
4. Done. The AI learns it automatically.
