# ArunCore: High-Level System Design

This document outlines the production architecture, component interactions, and data flow for the ArunCore personal AI assistant.

---

## 🏗️ System Architecture Diagram

```mermaid
graph TD
    User["User Interface<br/>(Next.js 16 • Voice Studio TTS/STT)"] -->|HTTP /chat NDJSON| API["FastAPI Web Server<br/>(Local :8000 / HF Docker :7860)"]
    
    %% Intent & Tool Routing
    API --> Agent["Agentic Execution Loop<br/>(LLM: gpt-4.1-nano)"]
    
    Agent -->|Tool: search_arun_knowledge| HybridRAG["Hybrid RAG Pipeline"]
    Agent -->|Tool: get_github_live_data| GitHubAPI["GitHub Live API"]
    Agent -->|Tool: notify_arun| TelegramAlert["Dual Telegram Engine<br/>(@ai_twin_alert_bot)"]

    %% Hybrid RAG Pipeline
    subgraph Hybrid RAG Pipeline
        HybridRAG --> Dense["ChromaDB Vector Search<br/>(text-embedding-3-small)"]
        HybridRAG --> Sparse["BM25 Keyword Matching"]
        Dense --> Combine["Candidate Assembly (Top 20)"]
        Sparse --> Combine
        Combine --> Rerank["Cohere English V3 Reranker"]
        Rerank --> TopContext["High-Confidence Context (Top 3-5)"]
    end

    %% Value-First Synthesizer
    TopContext --> Synthesizer["Value-First Prompt Synthesizer<br/>(Problem Solved • Time Saved • Business Impact)"]
    GitHubAPI --> Synthesizer
    
    Synthesizer --> Agent
    Agent -->|Token Stream & Thoughts| API
    API -->|NDJSON Stream| User
    
    %% Voice Studio
    User -->|HTTP POST /tts| TTS["OpenAI Studio Neural Speech<br/>(tts-1 • alloy voice)"]
    TTS -->|Audio Buffer| User

    classDef db fill:#0F383E,stroke:#257A52,stroke-width:2px,color:#fff;
    classDef llm fill:#111726,stroke:#38BDF8,stroke-width:2px,color:#fff;
    classDef alert fill:#7C2D12,stroke:#F59E0B,stroke-width:2px,color:#fff;
    class HybridRAG,ChromaDB db;
    class Agent llm;
    class TelegramAlert alert;
```

---

## 📁 Component Breakdown

### 1. 💻 User Interface (Next.js 16 • Turbopack)
- **Default Light Mode**: Executive styling with high contrast tokens.
- **Voice Studio**:
  - **Speech-to-Text (STT)**: Real-time browser Microphone (`[ 🎙️ ]`) transcription.
  - **Text-to-Speech (TTS)**: High-definition neural studio voice button (`[ 🔊 Listen (HD Voice) ]`).
- **Real-Time NDJSON Streaming**: Token-by-token response rendering with live execution trace drawer.

### 2. 🌐 FastAPI Backend Server (`core/api.py`)
- Mounts Next.js static export (`frontend/out`) at root `/`.
- Exposes `/chat` (NDJSON token streaming) and `/tts` (audio synthesis).
- Operates on port `8000` locally and port `7860` inside Hugging Face Docker containers.

### 3. 🧠 Agentic Reasoning Core (`core/agent.py`)
- Powered by OpenAI's **`gpt-4.1-nano`** model ($0.05/1M input, $0.15/1M output).
- **Persona & Tone**: Casual, witty, cool-friend Indian boy vibe with zero corporate fluff.
- **Dynamic Language Matching**: Natural Hinglish for Hindi queries, clean articulate English for international/corporate queries.
- **Value & Problem-Solving First Rule**: On all project inquiries, the assistant leads with **real-world business value, problem-solving impact, and time/cost savings** before code specs.

### 4. 🔍 Hybrid RAG Pipeline
- **Dense Retrieval**: ChromaDB storing `text-embedding-3-small` vector embeddings.
- **Sparse Retrieval**: BM25 keyword matching.
- **Reranker Core**: **Cohere English V3 Reranker** filtering candidate chunks down to top 3–5 high-confidence snippets.

### 5. 🚨 Dual Telegram Alert & Logging Engine
- **Lead Alert Bot (`@ai_twin_alert_bot`)**: Fires instant phone alerts when visitors request hiring, consulting, or project collaborations.
- **Log Bot**: Asynchronously logs conversation transcripts and debug traces in the background.

### 6. 🐙 Live GitHub Engine (`get_github_live_data`)
- Fetches real-time public repositories, commit timestamps, and project activity directly from GitHub API.
