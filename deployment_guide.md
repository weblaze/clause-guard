# Clause-Guard Deploy Guide (Fresh Start)

Follow these steps to establish a clean, automated deployment pipeline using your GitHub repository.

## 1. Northern Frontend (Vercel)

Vercel will host your Next.js application and connect automatically to your GitHub repo.

1.  **New Project**: In Vercel, click **"Add New"** > **"Project"**.
2.  **Connect GitHub**: Select your `clause-guard` repository.
3.  **Project Settings**:
    *   **Root Directory**: Set this to `frontend`.
    *   **Framework Preset**: Keep as `Next.js`.
    *   **Production Branch**: Ensure this is set to `master`.
4.  **Environment Variables**: Add the following (get these from your Supabase Dashboard):
    *   `NEXT_PUBLIC_SUPABASE_URL`
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5.  **Deploy**: Click **"Deploy"**. Future pushes to GitHub will now auto-update this site.

---

## 2. Southern AI Engine (Railway)

Railway will host your FastAPI backend using the deterministic Docker configuration.

1.  **New Project**: In Railway, click **"New Project"** > **"Deploy from GitHub repo"**.
2.  **Connect GitHub**: Select your `clause-guard` repository.
3.  **Service Settings**:
    *   **Root Directory**: Keep this as `/` (the project root).
    *   **Deployment Branch**: Ensure Railway is watching the `master` branch.
    *   **Railway will automatically find the root `Dockerfile`**.
4.  **Environment Variables**:
    *   `PORT`: `8000` (Railway usually maps this automatically, but set it to be sure).
    *   `TESSERACT_PATH`: `/usr/bin/tesseract` (Pre-installed in the Docker image).
5.  **Deploy**: Railway will build and launch your backend.

---

## 3. Post-Migration Verification

Once both services are live:
1.  **Link Services**: Copy your Railway **Production URL** (e.g., `https://xxxx.up.railway.app`).
2.  **Frontend Update**: In your Vercel Dashboard, add a new environment variable:
    *   `NEXT_PUBLIC_API_URL`: [Your Railway Production URL]
3.  **Final Test**: Open the Vercel site, login via Google, and upload a PDF.

---

> [!TIP]
> **Database & Storage**: Since you are using Supabase, ensure your **RLS (Row Level Security)** policies allow authenticated users to upload and read from the `agreements` storage bucket and `reports` table.
