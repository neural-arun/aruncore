# ⚙️ Core Engine (`/core/`)

This folder contains the **Python backend engine** for Arun's AI Assistant. It handles the API server, AI reasoning loop, vector database search, OpenAI studio voice synthesis, real-time GitHub data fetching, and Telegram notifications.

---

## 📁 Files Overview & Descriptions

### 1. 🌐 `core/api.py` (FastAPI Web Server & Voice Endpoint)
- **What it does**: Runs the HTTP server on port 8000 that connects the frontend to the AI assistant.
- **Key Endpoints**:
  - `POST /chat`: Streams real-time AI responses token-by-token using NDJSON over HTTP.
  - `POST /tts`: Converts AI text into HD neural studio voice audio using OpenAI `tts-1` (`alloy` voice).
  - `GET /health`: Health check endpoint showing system status and active sessions.

---

### 2. 🧠 `core/agent.py` (AI Persona, Agentic Loop & Tools)
- **What it does**: Defines the AI assistant's system prompt, persona rules (witty, casual, cool-friend vibe with dynamic English/Hindi language matching), memory management, and tool functions.
- **Tools**:
  - `search_arun_knowledge`: Hybrid ChromaDB vector search + BM25 keyword matching + Cohere V3 reranker.
  - `get_github_live_data`: Fetches real-time public repositories and recent commit activity from GitHub.
  - `notify_arun`: Sends instant Telegram alerts to Arun's phone for hiring leads or urgent queries.
- **Memory**: `RollingMemory` compresses historical chat context after 4 turns using `gpt-4o-mini` to keep conversation context concise.

---

### 3. 📚 `core/ingest.py` (Vector Database Compiler)
- **What it does**: Scans all markdown and JSON files inside `data/`, chunks them into semantic paragraphs, generates vector embeddings using OpenAI (`text-embedding-3-small`), and stores them in ChromaDB (`db/`).

---

### 4. 🤖 `core/bot.py` (Public Telegram Bot Service)
- **What it does**: Runs a standalone Telegram bot service allowing visitors to interact with Arun's AI Assistant directly inside Telegram.
