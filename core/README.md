# ⚙️ Core Engine (`/core/`)

This folder contains the **Python backend engine** for ArunCore. It handles the API server, AI reasoning loop (`gpt-4.1-nano`), vector database search, OpenAI studio voice synthesis, real-time GitHub data fetching, dual Telegram notifications, and the **Active Learning Loop**.

---

## 📁 Files Overview & Descriptions

### 1. 🌐 `core/api.py` — FastAPI Web Server & Stream Engine
- Runs the async HTTP server (port `8000` locally, port `7860` on Hugging Face Spaces).
- **Key Endpoints**:
  - `POST /chat`: Streams real-time AI responses token-by-token (NDJSON) with execution trace thoughts.
  - `POST /tts`: Converts AI text into HD neural studio voice using OpenAI `tts-1` (`alloy` voice).
  - `GET /health`: Health check endpoint showing system status and active sessions.
- **Full Execution Trace Logging**: Every conversation logs to Telegram with tools called, retrieved context chunks, execution steps, and the final response.

---

### 2. 🧠 `core/agent.py` — AI Persona, Agentic Loop & Tools
- Configures the main LLM (`gpt-4.1-nano`), persona system prompt, and all tool functions.
- **Language Matching**: Strict English-only for English queries. Natural Hinglish/Hindi for Hindi queries. No mixing.
- **Tools**:
  - `search_arun_knowledge`: Alias-aware project search (resolves `MedCoach` → `med_coach/README.md`), always includes `public_profile.md` and checks `data/raw/unknown_questions.json` for Arun's verified human answers.
  - `get_github_live_data`: Fetches real-time public repositories and recent commit activity from GitHub.
  - `notify_arun`: Sends instant Telegram alerts (`@ai_twin_alert_bot`) for hiring leads, urgent queries, or unknown questions.
- **Unknown Questions Workflow**: When the AI can't answer, it alerts Arun AND asks the user for their Name, Email or Phone so Arun can follow up directly.
- **Active Learning**: `save_unknown_question_answer(question, answer)` appends verified Q&A pairs to `data/raw/unknown_questions.json` and triggers background re-ingestion.
- **Memory**: `RollingMemory` compresses historical context after 4 turns using `gpt-4.1-nano`.

---

### 3. 📚 `core/ingest.py` — Vector Database Compiler
- Scans all markdown and JSON files inside `data/`, chunks them semantically, generates vector embeddings (`text-embedding-3-small`), and compiles into ChromaDB (`db/`).
- **Smart JSON Parsing**: Specially parses `data/raw/unknown_questions.json` — each Q&A pair becomes its own searchable vector chunk.

---

### 4. 🤖 `core/bot.py` — Public Telegram Bot Service & Active Learning Handler
- Runs a standalone Telegram bot allowing visitors to interact with Arun's AI Assistant directly in Telegram.
- **Active Learning Reply Handler**: When Arun replies to an `UNKNOWN_QUESTION` or `ALERT` message in Telegram, the bot:
  1. Extracts the original user question from the alert message.
  2. Pairs it with Arun's reply as the verified answer.
  3. Saves it to `data/raw/unknown_questions.json`.
  4. Triggers background ChromaDB re-ingestion.
  5. Sends Arun a confirmation: *"✅ Answer Saved & Ingested into AI Memory!"*

---

### 5. 🧪 `core/evaluate.py` — Evaluation & Benchmarking Engine
- Runs stress-test benchmark evaluations against test sets to measure retrieval precision and generation quality.
