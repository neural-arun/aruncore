# ⚙️ Core Engine (`/core/`)

This folder contains the **Python backend engine** for Arun's AI Assistant. It handles the API server, AI reasoning loop (`gpt-4.1-nano`), vector database search, OpenAI studio voice synthesis, real-time GitHub data fetching, and dual Telegram notifications.

---

## 📁 Files Overview & Descriptions

### 1. 🌐 `core/api.py` (FastAPI Web Server & Static UI Host)
- **What it does**: Runs the async HTTP server (port `8000` locally, port `7860` on Hugging Face Spaces) that powers the backend API and serves the Next.js static UI export (`frontend/out`).
- **Key Endpoints**:
  - `POST /chat`: Streams real-time AI responses token-by-token using NDJSON with execution trace thoughts.
  - `POST /tts`: Converts AI text into HD neural studio voice audio using OpenAI `tts-1` (`alloy` voice).
  - `GET /health`: Health check endpoint showing system status and active sessions.

---

### 2. 🧠 `core/agent.py` (AI Persona, Agentic Loop & Tools)
- **What it does**: Configures the main LLM (`gpt-4.1-nano`), persona rules (witty, casual, cool-friend vibe with dynamic Hinglish/English language matching), **Value & Problem-Solving First** project rules, and tool functions.
- **Tools**:
  - `search_arun_knowledge`: Hybrid ChromaDB vector search + BM25 keyword matching + Cohere V3 reranker.
  - `get_github_live_data`: Fetches real-time public repositories and recent commit activity from GitHub.
  - `notify_arun`: Sends instant Telegram alerts to Arun's phone (`@ai_twin_alert_bot`) for hiring leads or urgent queries.
- **Memory**: `RollingMemory` compresses historical chat context after 4 turns using `gpt-4.1-nano` to keep conversation context concise.

---

### 3. 📚 `core/ingest.py` (Vector Database Compiler)
- **What it does**: Scans all markdown and JSON files inside `data/`, chunks them into semantic paragraphs, generates vector embeddings using OpenAI (`text-embedding-3-small`), and compiles them into ChromaDB (`db/`).

---

### 4. 🤖 `core/bot.py` (Public Telegram Bot Service)
- **What it does**: Runs a standalone Telegram bot service allowing visitors to interact with Arun's AI Assistant directly inside Telegram.

---

### 5. 🧪 `core/evaluate.py` (Evaluation & Benchmarking Engine)
- **What it does**: Runs stress-test benchmark evaluations against test sets to measure retrieval precision and generation quality.
