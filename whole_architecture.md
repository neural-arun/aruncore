# ArunCore: Complete System Blueprint & Master Architecture

This document presents the complete architectural specification for **ArunCore** — a production-grade, stateful, agentic portfolio and AI assistant.

---

# Phase 0: Core Philosophy & Answer Policy

ArunCore is NOT a generic chatbot wrapper; it is a **Grounded Reasoning Engine** governed by strict rules.

### 1. The Answer Policy (Enforced via System Prompt):
1. **Never Invent or Inflate:** Do not hallucinate impact, fake USMLE scores, or invent metrics.
2. **"I Don't Know" is Valid:** If retrieval confidence is low, the agent states it doesn't have the info and offers to ping Arun directly.
3. **Value & Problem-Solving First:** On project inquiries, lead with **WHAT problem it solves, HOW MUCH time/cost it saves, and THE REAL BUSINESS IMPACT** before code details.
4. **Dynamic Language Matching:** Clean, articulate English for corporate/international queries; natural Hinglish for Hindi chats.
5. **Witty Cool-Friend Tone:** Casual, fun, straightforward Indian boy vibe with zero corporate bakchodi.

### 2. Source of Truth Conflict Resolution:
If data conflicts arise, the priority hierarchy is **absolute**:
1. **Live API Data (Highest):** Wins for current state (e.g., "What is Arun's latest commit on GitHub?").
2. **Static Identity (Middle):** Wins for core philosophy, contact info (+91 8881109193), and strategic principles (`public_profile.md`).
3. **Vector Memory (Lowest):** Used for project documentation and historical descriptive context (`data/github/`).

---

# Phase 1: Data Architecture & Storage Layers

### A. The Static Knowledge Layer
- `data/static/public_profile.md` (Bio, technical skills, enriched project value specs, contact info).
- `data/static/rules_of_engagement.md` (System prompts, guardrails, and answer policies).
- `data/linkedin/profile_summary.md` (Synced LinkedIn technical write-ups and posts).

### B. The Dynamic Knowledge Layer (Vector DB)
- **Vector Database**: ChromaDB (`db/`) with `text-embedding-3-small` embeddings.
- **Sparse Index**: BM25 keyword matching engine.
- **Schema Metadata per Chunk**:
  - `source`: File path (e.g., `data/github/legal_RAG_system/README.md`)
  - `project_name`: Repository name
  - `tech_stack`: Array of languages/frameworks used
  - `url`: Clickable GitHub link

---

# Phase 2: Retrieval, Routing & Execution Loop

```
┌─────────────────────────────────────────────────────────────┐
│                       User Query                            │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                Agentic Execution Loop                       │
│                 (LLM: gpt-4.1-nano)                         │
└──────────────┬───────────────┼───────────────┬──────────────┘
               │               │               │
      [search_arun_knowledge] [get_github_live] [notify_arun]
               │               │               │
┌──────────────▼──────────────┐│        ┌──────▼──────────────┐
│  Hybrid RAG (Chroma + BM25) ││        │ Dual Telegram Engine│
│   + Cohere V3 Reranker      ││        │ (@ai_twin_alert_bot)│
└──────────────┬──────────────┘│        └─────────────────────┘
               │               │
┌──────────────▼───────────────▼──────────────────────────────┐
│              Value-First Prompt Synthesizer                 │
│       (Problem Solved • Time Saved • Business Value)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             Real-Time Token Stream (NDJSON)                 │
└─────────────────────────────────────────────────────────────┘
```

---

# Phase 3: The Production Tech Stack

| Layer | Component | Specification |
| :--- | :--- | :--- |
| **LLM Engine** | OpenAI `gpt-4.1-nano` | Ultra-low latency, $0.05/1M input, $0.15/1M output |
| **Embedding Model** | OpenAI `text-embedding-3-small` | 1536-dimensional dense vector embeddings |
| **Vector DB** | ChromaDB (`db/`) | Persistent vector store with metadata filtering |
| **Keyword Search** | BM25 Engine | Sparse keyword indexing for exact technical term recall |
| **Reranker Engine** | Cohere English V3 | Cross-encoder reranking candidate chunks to top 3–5 |
| **Voice Studio** | OpenAI `tts-1` (`alloy` voice) & Web Speech | HD Neural Speech synthesis (`/tts`) & Speech-to-Text (`[ 🎙️ ]`) |
| **Frontend Framework**| Next.js 16 (Turbopack) | React 19, Tailwind CSS, Lucide icons, forced Light Mode default |
| **Backend Server** | FastAPI (Python 3.11) | Async HTTP server with NDJSON streaming (`/chat`) |
| **Alert Engine** | Telegram Bot API | Dual bots: `@ai_twin_alert_bot` (Leads) + Background Chat Logger |
| **Hosting** | Hugging Face Spaces & Vercel | HF Docker Space (port 7860) & Vercel (`aruncore.vercel.app`) |

---

# Phase 4: Evaluation & Maintenance Workflows

1. **30-Question Stress-Test Benchmark**:
   - Run `PYTHONPATH=. python scripts/evaluate_30_questions.py` to evaluate responses across Identity, Live GitHub, RAG Projects, LinkedIn Insights, Lead Handoffs, and Safety Guardrails.
   - Results saved to [`test_output_30.json`](file:///home/arun/projects/profile/test_output_30.json).

2. **Master Operations Guide**:
   - Refer to [`OPERATIONS_GUIDE.md`](file:///home/arun/projects/profile/OPERATIONS_GUIDE.md) for step-by-step instructions on updating LinkedIn data, syncing GitHub repos, and deploying code updates.