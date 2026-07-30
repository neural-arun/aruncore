# 📊 Knowledge Base Data Directory (`/data/`)

This folder serves as the **single source of truth knowledge base** for Arun's AI Assistant. The ingestion engine (`core/ingest.py`) indexes these files into ChromaDB vector memory.

---

## 📁 Subdirectories & File Descriptions

```
data/
├── static/
│   ├── public_profile.md      # Core identity, contact info, detailed project value specs, stack & career overview
│   └── rules_of_engagement.md # Behavioral rules, safety boundaries, and response guidelines
├── github/                    # 22+ curated markdown repositories detailing Arun's projects & code
│   └── [project_name]/        # README.md and metadata.json for each individual repository
└── linkedin/
    └── profile_summary.md     # Scraped LinkedIn posts, insights, and engagement metrics
```

---

## 📁 Detailed File Overview

### 1. `data/static/public_profile.md`
- **What it does**: Defines Arun Yadav's background, contact details (+91 8881109193, `neural.arun.dev@gmail.com`), core engineering philosophy, specialization in Healthcare & Education AI systems, detailed project specs (Legal RAG IPC chunking, MedCoach reasoning tutor, NEET 10,000+ MCQs, 99acres scraper), and LinkedIn insights (Uday BPSC Rank 5, FastAPI Todo API).

### 2. `data/static/rules_of_engagement.md`
- **What it does**: Defines strict system instructions for the AI assistant (e.g. zero hallucination rules, when to cite GitHub repos, how to handle unknown questions, when to trigger lead alerts).

### 3. `data/github/` (Project Knowledge Base)
- **What it does**: Contains 22 individual subfolders for each of Arun's projects (e.g., `ArunCore`, `deep_research`, `legal_RAG_system`, `med_coach`, `neet-bot`). Each folder contains a detailed `README.md` and `metadata.json` for RAG vector retrieval.

### 4. `data/linkedin/profile_summary.md`
- **What it does**: Contains synced LinkedIn posts and articles written by Arun, allowing the AI assistant to reference his public technical thoughts and insights.
