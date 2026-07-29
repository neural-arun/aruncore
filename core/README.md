# Core Engine Module (`/core/`)

This directory houses the neural and structural Python backend of **ArunCore**. It manages API endpoints, LLM agent reasoning, vector database search, real-time GitHub inspection, and Telegram alerts.

---

## 🔑 Key Components

### `api.py` (FastAPI Server)
* **Framework:** FastAPI + `uvicorn`
* **Endpoint:** `POST /chat` (Streaming NDJSON), `GET /health`, `GET /test-telegram`
* **Function:** Serves real-time streaming responses (status updates, tool call thoughts, and final replies) to the Next.js client.

### `agent.py` (Reasoning Loop & Tools)
* **Framework:** LangChain & OpenAI (`gpt-4o-mini`).
* **Tool Bindings:**
  1. `search_arun_knowledge`: Hybrid ChromaDB + BM25 + Cohere Reranker search.
  2. `get_github_live_data`: Real-time GitHub engine (list repos, read READMEs, search commits, inspect raw code files).
  3. `notify_arun`: Telegram alert escalation for lead capture and urgent questions.
* **Memory:** `RollingMemory` compresses historical chat turns after 4 turns using GPT.

### `ingest.py` (Vector Database Compiler)
* **Framework:** LangChain Document Loaders + OpenAI Embeddings (`text-embedding-3-small`) + ChromaDB.
* **Function:** Crawls `../data/`, computes MD5 file hashes, chunks Markdown/JSON files, and incrementally updates the ChromaDB vector database in `../db/`.

### `bot.py` (Public Telegram Bot)
* **Framework:** `python-telegram-bot` + `ChatOpenAI`.
* **Function:** Allows users to talk directly to the ArunCore Digital Twin on Telegram.
