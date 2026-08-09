# 📊 ArunCore Data Directory (`data/`)

This directory contains the knowledge base, static profile documents, raw backgrounds, and GitHub repository README files used for retrieval-augmented generation.

---

## 📁 Data Subdirectories & Files

```text
data/
├── github/                    # 21 subdirectories containing raw README.md files for each repo
│   ├── aruncore/              # ArunCore RAG Engine README
│   ├── legal_RAG_system/      # Legal RAG System README
│   ├── med_coach/             # MedCoach Clinical Reasoning README
│   ├── neet-bot/              # NEET Medical Bot README
│   ├── real_state_listing_scraper/ # 99acres Scraper README
│   └── ... (21 total public repositories)
├── linkedin/
│   ├── posts.md               # Scraped public LinkedIn posts & technical insights
│   └── profile_summary.md     # Public LinkedIn profile summary
├── raw/
│   ├── personal_background.md # Deeper origin story, NEET pivot, JEE journey, & working style
│   └── unknown_questions.json # Verified Q&A store for active learning alerts
└── static/
    ├── public_profile.md      # Master public technical profile & architecture specs
    ├── rules_of_engagement.md # Steering rules, search mandates, & guardrails
    └── voice_persona.md       # Custom sharp & witty voice persona definition
```

---

## 🔄 Auto-Syncing Data

- **Sync GitHub READMEs**: `python3 scripts/sync_github.py`
- **Sync LinkedIn Posts**: `python3 scripts/sync_linkedin.py`
- **1-Click Master Sync**: `python3 scripts/sync_all.py`
- **Vector Ingestion**: `python3 scripts/ingest.py`
