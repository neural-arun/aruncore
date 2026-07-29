# 💻 Frontend Web Application (`/frontend/`)

This folder contains the **Next.js 16 (Turbopack) web application** for Arun's portfolio website and AI Assistant interface.

---

## 📁 Files & Directory Structure

```
frontend/
├── app/
│   ├── globals.css         # Custom CSS tokens, glassmorphism theme, and animation utilities
│   ├── layout.tsx          # Root HTML layout, font configurations, and default light theme wrapper
│   └── page.tsx            # Main state container managing active tab, streaming chat, and modals
├── components/
│   ├── Header.tsx          # Top navigation bar, tab switcher (Assistant, Projects, About), social links, theme toggle
│   ├── ChatPanel.tsx       # Landing view with 2x2 question cards, live streaming feed, STT Mic button, & HD TTS voice button
│   ├── ManifestoView.tsx   # About page detailing Arun's principles, technical skills, and engineering philosophy
│   ├── ProjectsView.tsx    # Filterable grid of 22+ projects with architecture summaries and live GitHub links
│   └── HandoffModal.tsx    # Interactive contact modal with quick links to WhatsApp, Email, Phone, & Telegram
├── lib/
│   └── types.ts            # TypeScript interfaces for Message, Project, and Chat API payloads
└── package.json            # Frontend dependencies and dev scripts
```

---

## 📁 Detailed File Descriptions

### 1. `app/page.tsx` (Main Application Entrypoint)
- **What it does**: Controls top-level application state. Handles NDJSON real-time token streaming from the FastAPI backend (`http://localhost:8000/chat`), manages message history state, and switches between views.

### 2. `components/Header.tsx` (Navigation Bar)
- **What it does**: Displays top navigation tab buttons ("AI Assistant", "Projects", "About"), profile badge, social media links (GitHub, LinkedIn, X), theme toggle switch, and "Contact" trigger button.

### 3. `components/ChatPanel.tsx` (Chat Interface & Voice Studio)
- **What it does**: The core interactive view. Contains:
  - **Symmetrical 100% Landing Card**: Hero photo card + 2x2 question prompt grid.
  - **Speech-to-Text (STT)**: Microphone button (`[ 🎙️ ]`) for voice-to-text input.
  - **Text-to-Speech (TTS)**: `[ 🔊 Listen (HD Voice) ]` button for high-quality audio output using OpenAI studio neural voice.
  - **Reasoning Trace Drawer**: Collapsible step-by-step engine execution drawer (`Cpu`).

### 4. `components/ManifestoView.tsx` (About Page)
- **What it does**: Renders Arun's engineering philosophy, operating principles, primary focus sectors (Healthcare & Education), and technical skills breakdown (Python, FastAPI, RAG, Agentic Architecture, LLM Evaluation, MCP).

### 5. `components/ProjectsView.tsx` (Portfolio Projects Grid)
- **What it does**: Displays a searchable, filterable grid of 22+ engineering projects with architecture descriptions, tech tags, and clickable GitHub source links.

### 6. `components/HandoffModal.tsx` (Contact Modal)
- **What it does**: Opens a modal popup with direct contact details (+91 8881109193, `neural.arun.dev@gmail.com`), one-click WhatsApp button, and quick inquiry form.

### 7. `lib/types.ts` (TypeScript Definitions)
- **What it does**: Provides strict TypeScript interfaces (`Message`, `Project`, `ChatRequest`, `ChatResponse`) to ensure clean type safety across components.
