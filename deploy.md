# 🚀 ArunCore — Production Deployment Guide

> **Architecture:** Next.js static frontend on **Vercel** + FastAPI backend on **Railway** +
> custom domain **neuralarun.in** (GoDaddy). Monorepo is deployed from GitHub
> (`neural-arun/aruncore`).

```
Browser (https://neuralarun.in)
└── Vercel  (serves frontend/out static export)
      └── calls ──> Railway  (FastAPI, uvicorn, port $PORT)
                      ├── OPENAI / COHERE / GITHUB / TELEGRAM keys (env)
                      └── volume /app/data  (persists active-learning answers)
```

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Push repository to GitHub](#2-push-repository-to-github)
3. [Deploy backend on Railway](#3-deploy-backend-on-railway)
4. [Deploy frontend on Vercel](#4-deploy-frontend-on-vercel)
5. [Point neuralarun.in (GoDaddy) to Vercel](#5-point-neuralarunin-godaddy-to-vercel)
6. [Verification checklist](#6-verification-checklist)
7. [Security notes](#7-security-notes)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites
- Accounts: [Railway](https://railway.app), [Vercel](https://vercel.com), [GoDaddy](https://godaddy.com) (domain `neuralarun.in`).
- All API keys available (from local `.env` — **never commit it**):
  - `OPENAI_API_KEY`, `COHERE_API_KEY`
  - `GITHUB_USERNAME`, `GITHUB_TOKEN`
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
  - `TELEGRAM_ALERT_BOT_TOKEN`, `TELEGRAM_ALERT_CHAT_ID`
  - `TELEGRAM_PUBLIC_BOT_TOKEN`, `ADMIN_SECRET_KEY`
  - `APIFY_API_TOKEN`, `LINKEDIN_PROFILE_URL` (optional)

---

## 2. Push repository to GitHub
```bash
cd /home/arun/projects/profile
git add -A
git commit -m "chore: production deploy prep"
git push origin main
```
This pushes the whole monorepo (backend + frontend + `data/` + `tenants/`). Railway and
Vercel each build only the part they need. `.env`, `db/`, and `frontend/out/` are gitignored.

---

## 3. Deploy backend on Railway
1. **railway.app → New Project → Deploy from GitHub repo** → `neural-arun/aruncore`.
2. Railway detects the **Dockerfile** and builds automatically.
   - Docker CMD already runs `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
3. **Variables** tab → add every key listed in [Prerequisites](#1-prerequisites).
   - Set `RUN_TELEGRAM_PUBLIC_BOT=true` only if you want the public Telegram bot process.
4. **Volumes** tab → add a volume mounted at **`/app/data`**.
   - Persists `data/raw/unknown_questions.json` (AI-trained answers). Without it, every
     redeploy resets learned answers. First mount is empty (seed it later if needed).
5. **Deploy**, then open **`https://<your-app>.up.railway.app/health`**.
   - Expected: `{"status": "ok", "active_sessions": {...}, "telegram_alert_bot_preview": "...", ...}`
   - Copy this URL — you'll need it for Vercel.

---

## 4. Deploy frontend on Vercel
1. **vercel.com → Add New → Project** → import `neural-arun/aruncore`.
2. **Root Directory** → `frontend`.
3. **Framework Preset** → Next.js. Output settings → Output directory → **`out`**
   (the project uses `output: "export"`; Vercel serves the static export).
4. **Environment Variables**:
   | Name | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_URL` | `https://<your-app>.up.railway.app` |
   | `NEXT_PUBLIC_TELEGRAM_ALERT_BOT_TOKEN` | your alert bot token |
   | `NEXT_PUBLIC_TELEGRAM_ALERT_CHAT_ID` | your alert chat id |
   - Without `NEXT_PUBLIC_API_URL` the chat falls back to `window.location.origin` and breaks.
5. **Deploy**. You get a `*.vercel.app` URL. CORS already allows `*` + all vercel.app subdomains.

---

## 5. Point neuralarun.in (GoDaddy) to Vercel
1. Vercel project → **Settings → Domains** → add `neuralarun.in` and `www.neuralarun.in`.
2. Choose **Vercel DNS**; Vercel shows the exact records to create.
3. In **GoDaddy DNS Manager**, create/replace:
   ```
   A      @      76.76.21.21
   CNAME  www    cname.vercel-dns.com
   ```
   Delete any conflicting `@` A/CNAME (e.g., old forwarding rows).
4. Vercel auto-provisions HTTPS. Propagation: minutes → up to 24h.

---

## 6. Verification checklist
- [ ] `https://<railway-url>/health` returns `status: ok`.
- [ ] `https://neuralarun.in` loads the hero card & tabs.
- [ ] Send a chat message → reply arrives, and **Telegram alert** fires.
- [ ] `?tutor=ed_donner` demo mode loads Ed Donner branding.
- [ ] Voice note (TTS) plays from the client.
- [ ] Redeploy does **not** wipe admin-verified answers (volume mounted).

---

## 7. Security notes
- **No secrets in code.** The alert bot token is read from
  `NEXT_PUBLIC_TELEGRAM_ALERT_BOT_TOKEN` (client env) — set it in Vercel only.
- If any token was ever committed or deployed publicly, **rotate it immediately**
  (Telegram: BotFather → revoke token), then update `Railway` + `Vercel` env.
- Future hardening: move client-side Telegram alerts behind a backend endpoint so the
  token never ships to the browser at all.

---

## 8. Troubleshooting
| Symptom | Fix |
| --- | --- |
| Chat calls Vercel URL, not Railway | Set `NEXT_PUBLIC_API_URL` on Vercel & redeploy |
| `/health` returns error on start | All Railway env vars present? `OPENAI_API_KEY` required at boot |
| Bot answers reset after redeploy | Volume `/app/data` not attached |
| Domain shows Vercel 404 | DNS not propagated / domain not added in Vercel settings |
| CORS errors in console | Backend `allow_origins=["*"]` already covers all; confirm deploy is newest |

---

## Optional upgrades
- Backend-only Dockerfile + `.dockerignore` → faster Railway builds (skip frontend build).
- Branded API subdomain: `api.neuralarun.in` → CNAME to your Railway app, then point
  `NEXT_PUBLIC_API_URL` at it.