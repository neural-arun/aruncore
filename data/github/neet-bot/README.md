---
project_name: neet-bot
github_url: https://github.com/neural-arun/neet-bot
language: HTML
stars: 0
topics: [None]
updated_at: 2026-07-26T01:35:53Z
---

# neet-bot

> **GitHub Repository:** [https://github.com/neural-arun/neet-bot](https://github.com/neural-arun/neet-bot)  
> **Primary Language:** HTML | **Stars:** 0 | **Forks:** 0  
> **Description:** No description provided.

---

# 🎓 NEET Preparation Platform & Telegram AI Multi-Bot System

An end-to-end, AI-powered preparation ecosystem for **NEET & JEE Mains** aspirants featuring **3 specialized Telegram bots** (Biology, Chemistry, Physics), an interactive **Web App**, an **AI Performance Diagnostic Engine**, and a curated dataset of **20,195 PYQs & NCERT questions** aligned with the latest official **NTA NEET Syllabus**.

---

## 🏗️ Architecture & How the Entire System Functions

The platform operates as a unified Python micro-service system designed for high availability, zero latency, and seamless multi-channel learning (Telegram + Web Browser).

```
                            ┌─────────────────────────────────────────┐
                            │            USER INTERFACES              │
                            └────────────────────┬────────────────────┘
                                                 │
                     ┌───────────────────────────┼───────────────────────────┐
                     ▼                           ▼                           ▼
          🤖 GPT Biology Bot            🧪 GPT Chemistry Bot         ⚡ GPT Physics Bot
          (Telegram Polling)            (Telegram Polling)           (Telegram Polling)
                     │                           │                           │
                     └───────────────────────────┼───────────────────────────┘
                                                 │
                                                 ▼
                                     🌐 Embedded Web App & API
                                     (Python HTTPServer on 8080)
                                                 │
          ┌──────────────────────────────────────┼──────────────────────────────────────┐
          ▼                                      ▼                                      ▼
  📁 Question Engine                    🤖 AI Diagnostic Mentor                📄 ReportLab PDF Generator
  (questions.py)                        (ai_analyzer.py - GPT-4o-mini)          (pdf_report.py)
  Loads 20,195 Questions                Analyzes Missed Concepts                Renders Full Solution Reports
          │                                      │                                      │
          └──────────────────────────────────────┼──────────────────────────────────────┘
                                                 │
                                                 ▼
                                     💾 SQLite Database (db.py)
                                     Tracks Scores, Analytics & Users
```

---

## 🚀 How the System Works Step-by-Step

### 1. Multi-Bot Engine (`neet_bot/main.py`)
* The core entry point launches background threads for 3 Telegram bots concurrently:
  * **GPT Biology Bot**: Serves 11,279 Biology questions across 32 active NTA chapters.
  * **GPT Chemistry Bot**: Serves 4,392 Chemistry questions across 18 active NTA chapters.
  * **GPT Physics Bot**: Serves 4,524 Physics questions across 20 active NTA chapters.
* Runs a multi-port health and HTTP server (`0.0.0.0:8080`) providing live web app interfaces and diagnostic APIs for Railway / Cloud deployment.

### 2. Interactive Chapter Test Flow
* **Chapter Selection**: Students choose any NCERT chapter or custom multi-chapter mock test.
* **Inline Practice & Timer**: Questions are served with interactive Telegram inline keyboards or Web UI buttons.
* **Instant Verification & Scoring**: Tracks correct/wrong answers, time spent, and detailed option choices.

### 3. AI Performance Diagnostics (`ai_analyzer.py`)
* When a test is finished, the AI Diagnostic Engine evaluates the student's missed questions using OpenAI's `gpt-4o-mini` model.
* Generates a personalized diagnostic report highlighting **Core Weak Topics**, **Key Misconceptions**, and an **Actionable NCERT Revision Plan**.

### 4. Automated Detailed PDF Report Cards (`pdf_report.py`)
* Generates a downloadable PDF report card featuring:
  * Overall score, percentage, and time taken.
  * Question-by-question breakdown showing student choice vs correct answer.
  * **💡 Detailed Step-by-Step Solutions** with mathematical derivations and key NCERT memory tips.

---

## 📂 Repository Directory Guide

| Directory / File | Description & Functionality |
| :--- | :--- |
| **[`neet_bot/`](file:///home/arun/projects/neet_pp/neet_bot)** | **Master NEET Multi-Bot Engine**. Contains the combined bot runner, web app server, AI analyzer, SQLite database driver, and report card generator. |
| **[`chemistry_bot/`](file:///home/arun/projects/neet_pp/chemistry_bot)** | Dedicated Chemistry Bot module configured for 4,392 NEET & JEE Mains Chemistry questions. |
| **[`physics_bot/`](file:///home/arun/projects/neet_pp/physics_bot)** | Dedicated Physics Bot module configured for 4,524 NEET & JEE Mains Physics questions. |
| **[`dataset/`](file:///home/arun/projects/neet_pp/dataset)** | Master dataset folder containing 20,195 JSON and JSONL question banks organized by subject and NTA chapter. |
| **[`Dockerfile`](file:///home/arun/projects/neet_pp/Dockerfile)** | Docker container build recipe configured for Railway and cloud deployments. |
| **[`requirements.txt`](file:///home/arun/projects/neet_pp/requirements.txt)** | Python dependencies (`python-telegram-bot`, `openai`, `reportlab`, `apscheduler`). |
| **[`nixpacks.toml`](file:///home/arun/projects/neet_pp/nixpacks.toml)** | Railway fallback build specification. |

---

## 🛠️ Local Development & Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/neural-arun/neet-bot.git
cd neet-bot

# 2. Set up virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment variables in .env
# BIOLOGY_BOT_TOKEN=your_token
# CHEMISTRY_BOT_TOKEN=your_token
# PHYSICS_BOT_TOKEN=your_token
# OPENAI_API_KEY=your_openai_key

# 4. Start the Master Multi-Bot Engine
python3 neet_bot/main.py
```