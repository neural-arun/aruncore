# 🎨 ArunCore Frontend Architecture (`frontend/`)

> **Framework:** Next.js 16 (App Router)  
> **Styling:** Vanilla CSS Tokens (`globals.css`)  
> **UI System:** Luxury Dark/Light Mode with Glowing Accent Borders & Dynamic Brand Injections  

---

## 📁 Frontend Directory Map

```text
frontend/
├── app/
│   ├── layout.tsx             # Main HTML Root Layout & Metadata
│   ├── page.tsx               # Primary Application View (100% Dynamic Tutor URL Resolver)
│   └── globals.css            # Design System CSS Variables & Utility Classes
├── components/
│   ├── Header.tsx             # Brand Header, Theme Switcher, URL parameters
│   ├── ChatPanel.tsx          # Interactive ReAct Chat Interface & Message List
│   ├── ProjectsView.tsx       # Interactive Grid of Featured GitHub Projects
│   ├── ManifestoView.tsx      # System Philosophy & Engineering Architecture View
│   ├── Sidebar.tsx            # Contact Info, Social Links, & Live Human Status Indicator
│   ├── VoiceRecorder.tsx      # Audio Recording Mic Button & STT Interface
│   └── HandoffModal.tsx       # Live 3-Way Human Chat Takeover Room Modal
└── public/
    ├── ed_donner.png          # High-Res Avatar for Ed Donner Demo
    └── profile_photo.png      # High-Res Avatar for Arun Yadav
```

---

## 🎨 Dynamic Brand Theme System

The frontend automatically resolves custom brand themes passed via `/api/v1/config?tutor=<tutor_id>`:

```css
:root {
  --accent-green: #10b981;
  --accent-green-hover: #059669;
  --border-accent: rgba(16, 185, 129, 0.3);
  --bg-accent-soft: rgba(16, 185, 129, 0.1);
}
```

When visiting `?tutor=ed_donner`, the frontend dynamically overrides CSS variables to match Ed Donner's Deep Teal (`#0d9488`) brand theme while keeping 100% of layout structure, headers, tabs, and components intact!

---

## 🚀 Running Frontend Locally

```bash
cd frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.
