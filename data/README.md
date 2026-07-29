# Knowledge Base (`/data/`)

This directory is the single source of truth for ArunCore's semantic memory.

---

## 📁 Directory Structure

```
data/
├── static/
│   ├── public_profile.md         # Core identity, principles, vision & system loop
│   └── rules_of_engagement.md   # Zero-hallucination rules & system prompts
│
├── github/                        # Curated project repositories
│   ├── <project_name>/
│   │   ├── README.md              # Project README with direct GitHub URL
│   │   └── metadata.json          # Repo metadata (language, stars, topics)
│   └── ... (22 synced repos)
│
├── linkedin/
│   └── posts.md                   # Auto-scraped LinkedIn posts and technical insights
│
└── HOW_TO_UPDATE_DATA.md          # Guide for updating data in the future
```

---

## 🔄 Quick Commands

* **Sync All 22 GitHub Repos & READMEs:**
  ```bash
  python scripts/sync_github_data.py
  ```
* **Sync LinkedIn Posts & Re-Ingest Vector DB:**
  ```bash
  python scripts/sync_linkedin.py
  ```
* **Re-Ingest Vector DB Manually:**
  ```bash
  python core/ingest.py
  ```
