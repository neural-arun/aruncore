# 🤖 AGENTS.md — Master Protocol & Execution Rules for AI Coding Agents

> **IMPORTANT**: Any coding agent or LLM-assisted development tool (Antigravity, Claude, Cursor, Copilot, etc.) working on this repository **MUST** read this file and follow every rule strictly.
> **ARCHITECTURE VERSION**: ❄️ **v1.0 FROZEN** (Official Release Specification)

---

## 🎯 Project Mission
ArunCore is a domain-generic, multi-tenant enterprise AI platform.
Your primary objective is **NOT** to maximize code generation.
Your primary objective is to **preserve architectural integrity by default while implementing the smallest correct change**.
If a requested feature requires architectural changes, explain the tradeoffs and ask for user confirmation before proceeding.

---

## 🔝 Priority Order (Highest → Lowest)
When resolving conflicts, follow this exact hierarchy:
1. 👤 **User explicit instructions**
2. 📄 **AGENTS.md** (Master Protocol & Rules)
3. 📐 **aruncore_master_blueprint.md** (Architecture Specification)
4. 📂 **understanding_each_folder/** (Technical Folder Guides)
5. ⚙️ **Existing Codebase**

---

## 📜 File Reading Priority
Always inspect files in this exact hierarchy before modifying code:
1. 📄 Master Architecture Spec: [`aruncore_master_blueprint.md`](file:///home/arun/projects/profile/aruncore_master_blueprint.md)
2. 📂 Folder Technical Guides: [`understanding_each_folder/README.md`](file:///home/arun/projects/profile/understanding_each_folder/README.md)
3. 📋 Validation Schemas: `backend/app/schemas/` (`tenant.py`, `chat.py`)
4. ⚙️ Source Code: `backend/app/` or `frontend/`
5. 🧪 Test Suite: `tests/`

---

## 🏛️ The 11 Golden Architecture Principles (NON-NEGOTIABLE)

1. 🥇 **Preserve Current Frontend 100%**: Absolutely DO NOT replace or alter the existing Next.js frontend UI (`frontend/app/page.tsx`, `frontend/components/ChatPanel.tsx`, `ProjectsView.tsx`, `ManifestoView.tsx`, `Header.tsx`). The existing luxury UI, design tokens, glowing accent borders, light/dark themes, hero assistant card, and tab views stay 100% intact!
2. 🥈 **Zero Functionality Loss (Keep & Enhance)**: DO NOT remove a single working feature from the current app (Hybrid RAG, Telegram active learning alerts, 3-way live human chat presence, TTS neural voice, admin mode, session history). The goal is to keep 100% of existing functionality and upgrade it to production grade!
3. 🥉 **Production-Grade Hybrid RAG Engine**: Maintain and enhance the hybrid RAG architecture (dense ChromaDB vector search + sparse BM25 keyword search + Cohere/LLM reranking) for ultra-fast, high-precision knowledge retrieval per tenant.
4. 🏅 **Ultra-Simple Demo System**: Demo mode operates by passing a URL query parameter (`?tutor=ed_donner` or `?client=ed_donner`). The frontend fetches metadata from `/api/v1/config?tutor=ed_donner` (or `/config?tutor=ed_donner`), which dynamically populates the existing hero card title, role subtitle, avatar, welcome text, suggested questions, and AI system prompt. Zero complex slot engines required!
5. 🏅 **Explicit `tenants/` Directory**: All raw PDFs, markdown files, avatars, logos, and vector databases live in `./tenants/` outside the Git code repo. Keep code repos lightweight (~10MB).
6. 🏅 **Split Targeted Config**: Tenant configs in `tenants/<id>/config/` are split into 6 targeted JSON files (`brand.json`, `agent.json`, `chat.json`, `voice.json`, `seo.json`, `social.json`). Easy debugging, zero merge conflicts, Pydantic validated.
7. 🏅 **ZERO Backend Client `if` Statements**: Absolutely NO `if client == "ed":` or `if tenant_id == "hitesh":` statements anywhere in Python code! All tenant logic, prompts, tools, and branding MUST be resolved dynamically by `TenantService`.
8. 🏅 **Config-Driven Tool Registry**: Client tools are controlled via the `enabled_tools` array in `agent.json` (`["search_courses", "book_calendar", "faq_lookup"]`). `ToolExecutor` dynamically binds enabled tools into the LLM execution loop—zero Python code edits required!
9. 🏅 **Separation of Tenant Assets**: Static brand images (`tenants/<id>/assets/avatars/`, `tenants/<id>/assets/logos/`) are kept separate from code logic.
10. 🏅 **Decoupled Single-Responsibility Services**: Maintain small, focused backend services (`PromptBuilder`, `MemoryManager`, `ToolExecutor`, `AgentRunner`, `RAGService`, `NotificationService`, `ActiveLearningService`). Do NOT create monster monolithic service files.
11. 🏅 **Interface Abstractions**: Use abstract base classes for adapters (`VectorStore`, `StateStore`, `NotificationProvider`). Never hardcode direct dependencies in business logic.

---

## ⚙️ Required Execution Workflow

1. **Understand**: Read the task and relevant architecture docs.
2. **Locate**: Identify the exact affected files.
3. **Plan**: If the change affects >5 files, public APIs, schemas, or architecture -> create a plan first. Do NOT write code immediately.
4. **Minimal Change**: Apply the smallest possible correct change. Prefer modifying existing code over spawning new modules.
5. **Verify**: Run automated tests (`python3 -m unittest discover -s tests`).
6. **Update Docs**: Immediately update both `aruncore_master_blueprint.md` AND `understanding_each_folder/` guides.
7. **Self-Review**: Review your diff against the pre-completion checklist.

---

## ❓ Ask Before Proceeding

Always ask for user confirmation before:
- Deleting files or modules.
- Renaming large directories.
- Changing public API contracts or endpoints.
- Modifying validation schemas or database structures.
- Changing authentication, security, or permissions logic.
- Modifying package dependencies or build tooling.

---

## 🛑 When NOT to Code (Escalation Triggers)

Stop coding immediately, explain the conflict, and ask for clarification when:
- Architecture or requirements are unclear.
- API contracts or schemas are missing.
- The request contradicts any Golden Principle or blueprint specification.

---

## ❌ "Never Do These" (Strict Ban List)

Never:
- Alter or replace the existing Next.js frontend UI layout, headers, tabs, or design system.
- Remove or degrade existing working features (RAG, Telegram alerts, TTS, active learning loop, admin mode).
- Invent APIs, schemas, environment variables, endpoints, or tenant configs without authoritative source definitions.
- Write hardcoded `if client == "..."` logic anywhere in Python code.
- Wrap failing logic in silent `try/except: pass` or return dummy empty fallbacks.
- Skip verification commands or leave TODO implementations.
- Rename large directories, reformat unrelated files, or modify package lockfiles unless explicitly requested.
- Hardcode secrets, log tokens/API keys, or disable validation/authentication.
- Introduce N+1 database queries, blocking I/O on main loops, or redundant vector searches.

---

## 🔒 Minimal Change Principle
- Prefer modifying existing code over creating new abstractions.
- Only create new modules or files when strictly necessary. Avoid spawning unnecessary files.

---

## ✅ Definition of "DONE"

A task is complete ONLY if:
- [ ] Code compiles and builds cleanly without warnings.
- [ ] Existing Next.js frontend UI is 100% preserved and functional.
- [ ] 100% of existing capabilities (Hybrid RAG, Telegram active learning, TTS, 3-way chat) remain fully intact.
- [ ] Verification tests pass (`python3 -m unittest discover -s tests`).
- [ ] Both `aruncore_master_blueprint.md` AND `understanding_each_folder/` guides are fully updated.
- [ ] No Golden Architecture Principles are violated.
- [ ] No dead code, commented-out blocks, or unused imports remain.

---

## 📋 Pre-Completion Review Checklist

Before marking any task complete, verify:
- [ ] **Frontend Preserved**: Existing UI layout, tabs (`Chat`, `Projects`, `Manifesto`), design tokens, and components are 100% intact.
- [ ] **Features Retained**: Zero feature removals (Hybrid RAG, Telegram alerts, TTS, active learning loop preserved).
- [ ] **Architecture preserved**: Zero `if client == ...` checks, clean backend decoupling.
- [ ] **Minimal diff**: No unrelated files edited or reformatted.
- [ ] **Type safety**: Pydantic validation used in backend; explicit TypeScript interfaces used in frontend.
- [ ] **Documentation synced**: Blueprint and folder guides match the diff.
- [ ] **Tests verified**: Test suite passed with zero errors.
