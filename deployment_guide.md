# Clause-Guard Deploy Guide (Fresh Start)

Follow these steps to establish a clean, automated deployment pipeline using your GitHub repository.

## 1. Frontend (Vercel)

Vercel will host your Next.js application and connect automatically to your GitHub repo.

1.  **New Project**: In Vercel, click **"Add New"** > **"Project"**.
2.  **Connect GitHub**: Select your `clause-guard` repository.
3.  **Project Settings**:
    *   **Root Directory**: Set this to `frontend`.
    *   **Framework Preset**: Keep as `Next.js`.
    *   **Production Branch**: Ensure this is set to `master`.
4.  **Environment Variables**: Add the following once your Render backend is live (see Section 2):
    *   `NEXT_PUBLIC_BACKEND_URL`: Your Render backend URL.
5.  **Deploy**: Click **"Deploy"**. Future pushes to GitHub will now auto-update this site.

---

## 2. Backend (Render)

Render hosts the FastAPI backend using the same root `Dockerfile` and the `render.yaml` blueprint already committed to this repo.

1.  **New Blueprint**: In the Render dashboard, click **"New +"** > **"Blueprint"**.
2.  **Connect GitHub**: Select your `clause-guard` repository. Render will detect `render.yaml` at the repo root and pre-fill a `clause-guard-backend` web service (Docker runtime, free plan, health check on `/api/v1/health`).
3.  **Environment Variables**: `render.yaml` already sets sensible defaults for `GROQ_MODEL`, `GROQ_CONCURRENCY`, `CLAUSE_TIMEOUT_SECONDS`, `HYBRID_RETRIEVE_K`, `RERANK_TOP_K`/`RERANK_ENABLED`/`RERANK_MODEL`. You still need to fill in the variables marked `sync: false` — enter these directly in Render's Environment tab, never in chat or the repo:
    *   `GROQ_API_KEY`: Generate a free key at [console.groq.com](https://console.groq.com) (no card required).
    *   `DATABASE_URL`: A Postgres connection string for analysis history. [Neon](https://neon.tech) has a genuinely permanent free tier (unlike Render's own free Postgres, which expires after 30 days) — create a project, copy the connection string. If left unset, the app still works fully; it just skips writing history.
    *   `ALLOWED_ORIGINS` *(optional)*: comma-separated list of extra frontend origins allowed to call the API (e.g. a custom domain). Any `https://clause-guard*.vercel.app` origin and `http://localhost:3000` are always allowed by default.
    *   Want a different Groq model? Browse [console.groq.com/docs/models](https://console.groq.com/docs/models) — strict structured-output mode (used here) is currently only supported on `openai/gpt-oss-20b` and `openai/gpt-oss-120b`.
4.  **Deploy**: Render will build the Docker image and launch the backend. Note the assigned URL (e.g. `https://clause-guard-backend.onrender.com` — Render suffixes it if that name is already taken by someone else).

> [!NOTE]
> Render's free plan spins the service down after ~15 minutes of inactivity and cold-starts on the next request. The first request after idle time will be slow, since `RAGService` re-initializes ChromaDB and re-embeds the statute knowledge base on every boot.

---

## 3. Post-Deploy Verification

Once both services are live:
1.  **Copy the Render URL**: From the Render dashboard, copy your service's public URL.
2.  **Frontend Update**: In your Vercel Dashboard, add/update the environment variable:
    *   `NEXT_PUBLIC_BACKEND_URL`: [Your Render URL]
    *   Trigger a redeploy in Vercel so the new env var actually takes effect (env var changes don't apply retroactively to an already-built deployment).
3.  **Final Test**: Open the Vercel site, go straight to **Analyze**, and upload a PDF — no login required. If the backend just cold-started, the first request may take a while before you see a result.

---

## Alternative: Railway

This repo still contains `railway.json`, so Railway remains an option if you want to revisit it later. On Railway's free plan, deployments must run in **serverless mode** (toggle this in the service settings) — the same cold-start-on-idle trade-off as Render's free tier, just enforced as an explicit setting rather than a fixed timeout.
