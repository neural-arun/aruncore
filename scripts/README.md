# 🛠️ ArunCore Automated Scripts & Evaluation Harness (`scripts/`)

This directory contains automated maintenance scripts, data pipelines, and evaluation harnesses powering ArunCore.

---

## 📁 Script Inventory & Documentation

| Script File | Purpose | Description |
| :--- | :--- | :--- |
| **`evaluate.py`** | Multi-Turn ReAct Evaluation Harness | Reads test questions from `evaluation_questions.md`, runs full 7-iteration ReAct loop using `gpt-4.1-nano`, and writes output traces to `evaluation_results.md`. |
| **`evaluation_questions.md`** | 30 Evaluation Test Questions | Structured Markdown file containing all 30 test questions across 6 core categories. |
| **`evaluation_results.md`** | Evaluation Results & Traces | Stores full execution traces, tools used, timestamps, and AI answers for all 30 questions. |
| **`sync_github.py`** | GitHub API Auto-Sync | Queries GitHub API (`https://api.github.com/users/neural-arun/repos`), fetches raw `README.md` files for all public repos, and saves formatted markdown files to `data/github/<repo>/README.md`. |
| **`sync_linkedin.py`** | LinkedIn Posts Sync | Triggers Apify LinkedIn scraper integration and saves public LinkedIn posts into `data/linkedin/posts.md`. |
| **`sync_all.py`** | 1-Click Master Data Sync | Master runner executing `sync_github.py` and `sync_linkedin.py` in sequence. |
| **`ingest.py`** | ChromaDB Vector Re-Ingestion | Re-chunks and re-embeds all markdown files across `data/` into `db/chroma.sqlite3` using OpenAI `text-embedding-3-small`. |

---

## 🚀 How to Run Scripts

### Run 30-Question Evaluation Suite:
```bash
python3 scripts/evaluate.py
```

### Sync All GitHub Repositories:
```bash
python3 scripts/sync_github.py
```

### Run 1-Click Master Sync:
```bash
python3 scripts/sync_all.py
```

### Re-Build ChromaDB Vector Database:
```bash
python3 scripts/ingest.py
```
