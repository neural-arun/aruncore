# 💻 Frontend Web Application (`/frontend/`)

This folder contains the **Next.js 16 (Turbopack) web application** for Arun's portfolio website and AI Assistant interface. Supports both server-rendered dev mode and static HTML export (`output: "export"`) for Hugging Face Docker container hosting.

---

## 📁 Directory Structure

```
frontend/
├── app/
│   ├── globals.css         # Custom CSS tokens, glassmorphism theme, and animation utilities
│   ├── layout.tsx          # Root HTML layout, font configurations, and default light theme wrapper
│   └── page.tsx            # Main state container managing active tab, streaming chat, and modals
├── components/
│   ├── Header.tsx          # Top navigation bar, tab switcher (Assistant, Projects, About), social links, theme toggle
│   ├── ChatPanel.tsx       # Landing hero card + 2x2 prompt grid, STT Mic button, HD TTS voice button (mobile-optimized)
│   ├── ManifestoView.tsx   # About page: principles, technical skills, engineering philosophy
│   ├── ProjectsView.tsx    # Filterable grid of 22+ projects with architecture summaries and live GitHub links
│   └── HandoffModal.tsx    # Contact modal with quick links to WhatsApp, Email, Phone, & Telegram
├── lib/
│   └── types.ts            # TypeScript interfaces for Message, Project, and Chat API payloads
├── next.config.ts          # Static export config (`output: "export"`, `images.unoptimized: true`)
└── package.json            # Frontend dependencies and dev scripts
```

---

## 📁 Component Descriptions

### 1. `app/page.tsx` — Main Application Entrypoint
- Controls top-level application state.
- Handles NDJSON real-time token streaming from the FastAPI backend (`/chat`).
- Forces Light Mode default on load, manages message history state, and switches between views.

### 2. `components/Header.tsx` — Navigation Bar
- Top navigation tab buttons ("AI Assistant", "Projects", "About").
- Profile badge, social media links (GitHub, LinkedIn, X), theme toggle, and "Contact" trigger button.

### 3. `components/ChatPanel.tsx` — Chat Interface & Voice Studio
The core interactive view. Contains:
- **Symmetrical 100% Landing Card**: Hero photo card + 2x2 question prompt grid with live GitHub activity fetch card.
- **Speech-to-Text (STT)**: Microphone button (`[ 🎙️ ]`) for voice-to-text input.
  - **Duplicate-free transcription**: Fixed `baseTextRef` anchor correctly handles interim vs. final results — no more repeated text.
- **Text-to-Speech (TTS)**: `[ 🔊 Listen (HD Voice) ]` for HD audio using OpenAI studio neural voice.
- **Reasoning Trace Drawer**: Collapsible step-by-step engine execution drawer.
- **Mobile Optimized**: Full-width touch buttons, compact hero card (`p-3.5` padding), correct touch target sizes, sticky STT input container. Desktop/laptop layout is 100% unchanged.

### 4. `components/ManifestoView.tsx` — About Page
- Renders Arun's engineering philosophy, operating principles, primary focus sectors (Healthcare & Education), and technical skills breakdown.

### 5. `components/ProjectsView.tsx` — Portfolio Projects Grid
- Searchable, filterable grid of 22+ engineering projects with architecture descriptions, tech tags, and clickable GitHub source links.

### 6. `components/HandoffModal.tsx` — Contact Modal
- Opens a modal popup with direct contact details (+91 8881109193, `neural.arun.dev@gmail.com`), one-click WhatsApp button, and quick inquiry form.

### 7. `lib/types.ts` — TypeScript Definitions
- Strict TypeScript interfaces (`Message`, `Project`, `ChatRequest`, `ChatResponse`) for type safety across all components.

---

## 🚀 Running Locally

```bash
cd frontend
npm install
npm run dev       # Dev server at http://localhost:3000
npm run build     # Static export to frontend/out/ (for HF deployment)
```

---

## 🔗 API Configuration

Set the backend URL via environment variable:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000        # local dev
NEXT_PUBLIC_API_URL=https://neural-arun-aruncore.hf.space  # production (HF Spaces)
```
