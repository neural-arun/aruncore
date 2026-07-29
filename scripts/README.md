# 🛠️ Scripts & Data Automation (`/scripts/`)

This folder contains **Python utility and sync scripts** used to automate knowledge base updates from GitHub and LinkedIn.

---

## 📁 File Descriptions

### 1. 🐙 `scripts/sync_github_data.py`
- **What it does**: Connects to GitHub API, inspects all of Arun's public repositories (`neural-arun`), downloads fresh `README.md` files and metadata, and updates `data/github/` automatically.
- **How to run**:
  ```bash
  python scripts/sync_github_data.py
  ```

---

### 2. 💼 `scripts/sync_linkedin.py`
- **What it does**: Uses Apify API to fetch recent LinkedIn posts, articles, and engagement metrics from Arun's LinkedIn profile, and updates `data/linkedin/posts.md`. Automatically triggers re-ingestion into ChromaDB vector memory.
- **How to run**:
  ```bash
  python scripts/sync_linkedin.py
  ```
