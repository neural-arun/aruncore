# 🚀 Vercel + Railway Gold Standard Deployment Playbook
**ArunCore AI Agency Infrastructure Setup Guide**

This playbook provides a comprehensive, step-by-step master guide to deploy **ArunCore** from scratch using the industry-standard split cloud architecture:
- **Frontend (UI)**: Next.js 16 hosted on **Vercel** (Global Edge CDN, 0s cold start).
- **Backend (API)**: FastAPI Python Engine hosted on **Railway** (24/7 Always-On, 0s cold start).

---

## 🏛️ 1. Architecture & Core Concepts

### How the Split Architecture Works:

```
[ User Browser ]
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼ (HTTPS / HTML / JS)             ▼ (Streaming API / WebSockets / SSE)
┌──────────────────────────────┐  ┌──────────────────────────────┐
│       Vercel Edge CDN        │  │     Railway Cloud Engine     │
│   (Next.js Frontend UI)      │  │    (FastAPI Python Engine)   │
│   https://www.neuralarun.in  │  │   https://api.neuralarun.in  │
└──────────────────────────────┘  └──────────────────────────────┘
```

1. **Frontend (Vercel)**:
   - Serves static assets, React components, fonts, images, and HTML in `< 50ms` globally via Vercel's Edge Network.
   - Communicates with the backend using the `NEXT_PUBLIC_API_URL` environment variable.

2. **Backend (Railway)**:
   - Handles LLM streaming (`gpt-4o`), RAG vector database queries, memory management, TTS audio generation, and Telegram alerts.
   - Runs 24/7 with **zero sleep mode** and **zero cold starts**.

---

## 📋 2. Prerequisites & Preparation

1. **GitHub Repository**: Ensure your repository (`neural-arun/ArunCore`) is public and up to date.
2. **OpenAI API Key**: Obtain a valid API key (`sk-...`).
3. **Accounts Ready**:
   - [Railway.com](https://railway.com) Account
   - [Vercel.com](https://vercel.com) Account
   - [GoDaddy.com](https://godaddy.com) Account (Domain Registrar)

---

## 🛠️ PHASE 1: Deploy Backend API to Railway

### Step 1.1: Create New Railway Project
1. Log into [Railway.com](https://railway.com).
2. Click **`+ New Project`**.
3. Select **`Deploy from GitHub repo`**.
4. Search and select: **`neural-arun/ArunCore`**.

### Step 1.2: Configure Build & Start Command
1. Click on the newly created **`ArunCore`** service card.
2. Navigate to the **`Settings`** tab.
3. Under **Build Settings**:
   - Set **Builder**: `Nixpacks` (or `Dockerfile`).
4. Under **Deploy Settings**:
   - Set **Custom Start Command**:
     ```bash
     uvicorn core.api:app --host 0.0.0.0 --port $PORT
     ```

### Step 1.3: Add Environment Variables
1. Go to the **`Variables`** tab in Railway.
2. Add the following environment variables:
   - **`OPENAI_API_KEY`**: `sk-...` *(your OpenAI API key)*
   - **`PYTHONUNBUFFERED`**: `1`
3. Click **`Save`**. Railway will build and launch your backend container.

### Step 1.4: Generate Railway Public URL
1. Go to the **`Settings`** tab ➔ **`Networking`** section.
2. Click **`+ Custom Domain`** (or **`Generate Domain`**).
3. If using custom domain, enter: `api.neuralarun.in`.
4. Note your Railway public URL (e.g., `https://aruncore-production-xxxx.up.railway.app` or `https://api.neuralarun.in`).

---

## 🛠️ PHASE 2: Deploy Frontend UI to Vercel

### Step 2.1: Import Project to Vercel
1. Log into [Vercel.com](https://vercel.com).
2. Click **`Add New...`** ➔ **`Project`**.
3. Select and import your GitHub repository: **`neural-arun/ArunCore`**.

### Step 2.2: Configure Vercel Project Settings
1. **Framework Preset**: Next.js (Auto-detected).
2. **Root Directory**:
   - Click **`Edit`** next to Root Directory.
   - Type or select: **`frontend`**.
3. **Build & Output Settings**:
   - Build Command: `next build` (default)
   - Output Directory: `.next` (default)

### Step 2.3: Set Environment Variables
1. Under **Environment Variables**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://api.neuralarun.in` *(or your Railway URL `https://aruncore-production-xxxx.up.railway.app`)*
2. Click **`Deploy`**.
3. Vercel will build the Next.js application in ~45 seconds and provide a live `.vercel.app` URL.

---

## 🛠️ PHASE 3: Connect Custom Domain (`neuralarun.in`) on GoDaddy

### Step 3.1: Configure Backend Subdomain (`api.neuralarun.in`)
In GoDaddy DNS Management for `neuralarun.in`:
- **Type**: `CNAME`
- **Name**: `api`
- **Value**: `9oqf9wlm.up.railway.app` *(your Railway CNAME target)*
- **TTL**: `1 Hour`

### Step 3.2: Configure Frontend Main Domain (`www.neuralarun.in`)
1. In Vercel Project ➔ **`Settings`** ➔ **`Domains`**:
   - Add **`www.neuralarun.in`** and **`neuralarun.in`**.
2. In GoDaddy DNS Management:
   - **Type**: `CNAME`
   - **Name**: `www`
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: `1 Hour`
   - **Type**: `A`
   - **Name**: `@`
   - **Value**: `76.76.21.21`

---

## ✅ PHASE 4: Verification & Testing Checklist

Once DNS propagation finishes (~1-3 minutes):

| Verification Test | Target URL | Expected Result |
|---|---|---|
| **Frontend UI Test** | `https://www.neuralarun.in` | 🟢 Loads instant Next.js UI (< 50ms) |
| **Backend API Health Check** | `https://api.neuralarun.in/docs` | 🟢 FastAPI Swagger Docs load cleanly |
| **AI Stream Test** | Chat input on `https://www.neuralarun.in` | 🟢 Real-time token streaming with 0s cold start |
| **Telegram Alert Test** | Send test message in chat widget | 🟢 Immediate notification delivered to Telegram |

---

## 🔧 Troubleshooting & Common Issues

- **Issue: Frontend shows network error / backend not connecting**
  - *Fix*: Check Vercel Environment Variable `NEXT_PUBLIC_API_URL`. Ensure it matches your Railway API URL without a trailing slash, then click **Redeploy** on Vercel.

- **Issue: Railway backend shows 502 Bad Gateway**
  - *Fix*: Ensure Start Command uses `--port $PORT` so Uvicorn binds to Railway's assigned environment port.
