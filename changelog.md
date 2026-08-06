# Changelog - Clause-Guard

All notable changes to the **Clause-Guard** project will be documented in this file.

## [Session 1] - 2026-03-30
*Project Initialization and Foundation Setup*

### Completed
- **Git Initialization**:
  - Initialized repository with standard structure.
  - Created branches: `master`, `arunav`, `srishti`.
  - Switched to `arunav` for primary development.
- **Project Structure**:
  - Created `/backend` and `/frontend` directories.
  - Refined `.gitignore` for efficient GitHub experience (covers Python, Node, and Vector DB).
- **Backend Foundation**:
  - Created `requirements.txt` with essential dependencies (FastAPI, ChromaDB, Ollama, Tesseract).
  - Implemented `main.py` entry point with FastAPI and CORS.
  - Implemented `ocr_service.py` for Tesseract-based PDF text extraction.
  - Implemented `rag_service.py` for ChromaDB and Ollama-based clause analysis.
  - Implemented `clause_segmenter.py` for heuristic legal text splitting.
  - Implemented `risk_calculator.py` for weighted risk score calculation.
  - Implemented `models.py` for Pydantic schema consistency.
  - Initialized `knowledge_base.json` with Indian Model Tenancy Act 2021 clauses.
- **Firebase Cloud Transition (Phase 4 Started)**:
  - Initialized `firebase.ts` with the configuration for project `clause-guard-cf894`.
  - Configured `firebase.json` for Next.js Web App deployment.
  - Implemented `firestore.rules` and `storage.rules` for cloud-native security.
  - Targeted Firebase project `clause-guard-cf894` for Cloud native deployment.
  - Successfully committed all previous development progress for Phase 1/2 to the `arunav` branch.
  - Initialized backend Dockerization for Google Cloud Run (Linked to Firebase).
- **Version Control (Persistent Execution)**:
  - Implemented automatic Phase-based Git staging and committing as instructed.
  - Updated `.gitignore` for standard cloud/Next.js efficiency.

### Things To Do next session
- Complete frontend framework initialization.
- Implement the "Rich Aesthetic" Design System in CSS.
- Integrate the Backend RAG pipeline with actual Ollama inference.
- Develop the "Results Dashboard" UI component.

## [Session 2] - 2026-03-31
*Deployment Infrastructure and Backend Fixes*

### Completed
- **Dependencies Configuration**:
  - Resolved `ModuleNotFoundError: No module named 'langchain_community'` by adding missing requirements (`langchain-community`) to `requirements.txt`.
- **Backend Deployment**:
  - Replaced cloud provider embeddings with local **FastEmbed** to bypass provider restrictions on Railway.
  - Mapped generative AI core (**Gemma 3**) to communicate correctly with the remote Ollama API.
- **Frontend Connectivity**:
  - Corrected frontend Next.js environment variables to ensure successful end-to-end communication with the Railway backend for legal document analysis.
- **Branch Strategy & CI/CD**:
  - Migrated deployment tracking to the `master` branch for both Vercel and Railway.

## [Session 3] - 2026-08-06
*Auth Removal & Standalone Prototype Simplification*

### Completed
- **Removed Google/Supabase Auth**: The Google OAuth sign-in flow was unreliable in production (consent screen misconfiguration) and gated the entire product behind login. Authentication has been removed entirely from both the frontend and backend.
- **Removed Backend JWT Verification**: `verify_supabase_token` and the `/api/v1/analyze-url` endpoint (which required a Supabase JWT and a Supabase Storage URL) have been removed.
- **Removed Dead Auth Code**: Deleted `backend/auth_service.py`, a vestigial, unused JWT/bcrypt module left over from an earlier design that was never wired into the live app.
- **Removed Supabase Dependency Entirely**: Deleted `frontend/src/lib/supabase.ts` and `supabase_schema.sql`. The app no longer depends on Supabase for auth, storage, or persistence.
- **Fixed the Direct-Upload Endpoint**: `/api/v1/analyze` previously called an undefined function and was non-functional. It now correctly extracts text from the uploaded PDF via a new `OCRService.extract_text_from_file` method and runs the full analysis pipeline.
- **New Upload Flow**: The frontend now uploads the PDF directly to the FastAPI backend via `multipart/form-data` — no cloud storage bucket, no auth token, no login gate.
- **Stateless by Design**: Analysis results are returned directly to the client and are not persisted to any database.

### Result
The application now runs end-to-end — upload a PDF, get a risk report — with no external account setup required, out of the box.

## [Session 4] - 2026-08-06
*Post-Auth-Removal Cleanup and Security Hardening*

### Completed
- **Dependency Cleanup**: Removed `requests`, `openai`, `langchain-openai`, `supabase`, `python-magic`, and `python-jose[cryptography]` from `requirements.txt`, and `@supabase/supabase-js` from the frontend — none were referenced anywhere in the code after the auth removal.
- **CORS Tightened**: Replaced the wide-open `allow_origins=["*"]` with an explicit allowlist (`localhost:3000` plus any `*.vercel.app` deployment of this project, extendable via the `ALLOWED_ORIGINS` env var for a custom domain). Also dropped `allow_credentials=True`, which was never needed since the API doesn't use cookie-based auth.
- **Security Headers Added**: `/api/v1/analyze` and all other responses now include `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` headers.
- **Basic Rate Limiting**: Added a lightweight in-memory per-IP rate limiter (10 requests/minute) on `/api/v1/analyze` to blunt casual abuse of the OCR/LLM pipeline.

## [Session 5] - 2026-08-06
*Backend Migration: Railway to Render*

### Completed
- **Railway Free-Tier Issues**: Railway's free plan now requires deployments to run in serverless mode, and the service was found shut down/unreachable (`404 - the train has not arrived at the station`). Rather than continue fighting Railway's free-tier constraints, the backend was migrated to Render.
- **Added `render.yaml`**: A Render Blueprint reusing the existing root `Dockerfile` unchanged — Docker runtime, free plan, health check on `/api/v1/health`, with `OLLAMA_BASE_URL`/`OLLAMA_API_KEY`/`ALLOWED_ORIGINS` prompted as secrets at deploy time.
- **Updated Fallback URL**: The frontend's hardcoded backend fallback now points at the expected Render URL, though `NEXT_PUBLIC_BACKEND_URL` in Vercel remains the source of truth and must be set explicitly.
- **Docs & Copy Updated**: `deployment_guide.md`, `README.md`, and in-app branding copy now reference Render instead of Railway. Railway config (`railway.json`) was left in place as a documented fallback option rather than deleted.

## [Session 6] - 2026-08-06
*Portfolio-Grade RAG Architecture Rebuild (parked on `arunav`, not deployed to production)*

A real end-to-end test took 7 minutes to analyze one lease PDF. This session rebuilds the RAG pipeline from the ground up for speed, accuracy, and reliability, restructured as a proper demonstration of RAG and system-design practice. Everything below is committed to `arunav` only — the live `master`-tracked production deployment is untouched.

### Completed
- **Switched LLM provider: Ollama Cloud → Groq**. Ollama Cloud's free tier appears to serialize requests server-side (per its own pricing FAQ: "1 concurrent model, requests beyond the limit are queued"), making client-side parallelization largely pointless. Groq's LPU hardware gives genuinely low latency plus real concurrency, and its strict JSON-schema structured-output mode eliminates the previous regex-based JSON parsing entirely — `backend/rag/llm_provider.py` now wraps `AsyncGroq` behind a small `LLMProvider` interface (`openai/gpt-oss-20b`, retry/backoff on rate limits).
- **New `backend/rag/` package** replacing the old monolithic `rag_service.py`:
  - `retrieval.py` — hybrid retrieval: Chroma vector search + BM25 keyword search, fused via Reciprocal Rank Fusion, strictly scoped per jurisdiction (no more cross-jurisdiction fallback contamination now that every jurisdiction has real content).
  - `reranker.py` — local, free FastEmbed cross-encoder reranking (`RERANK_ENABLED` escape hatch for Render's 512MB free-tier RAM).
  - `graph.py` — a bounded, corrective-RAG-style cycle built on **LangGraph**: retrieve → grade (cheap heuristic, not a second LLM call) → conditionally rewrite-and-re-retrieve (max 1x) → generate → self-check the cited statute is actually grounded in the retrieved context → conditionally regenerate (max 1x) → finalize. Both loop-backs are hard-bounded so a stuck clause can never spin forever.
  - `cache.py` — exact-match in-memory cache skipping the whole retrieve→generate cycle for repeated/boilerplate clauses.
- **Fixed a second jurisdiction bug**: the "Central" jurisdiction option was *also* silently broken — the knowledge base tagged Central entries `"Central/Model"` while the API/frontend always sent `"Central"`, so exact-match filtering meant Central retrieved zero statutes too, not just Delhi/Maharashtra as previously found. Normalized to `"Central"` everywhere.
- **Async pipeline in `main.py`**: OCR now runs via `asyncio.to_thread` (previously blocked the event loop for the whole request); per-clause analysis runs concurrently via `asyncio.gather` + `asyncio.Semaphore(GROQ_CONCURRENCY)`, each with its own `asyncio.wait_for(..., timeout=CLAUSE_TIMEOUT_SECONDS)` — on timeout or failure, a clause is now explicitly flagged `analysis_failed=True` and defaults to `UNFAIR` for manual review, instead of silently reading as a genuinely fair clause.
- **Analysis history database**: `backend/db.py` adds SQLAlchemy async models (`AnalysisRun`, `ClauseResult`) against a Postgres `DATABASE_URL` (Neon's free tier recommended — Render's own free Postgres expires after 30 days). New `GET /api/v1/history` and `GET /api/v1/history/{session_id}` endpoints. Degrades gracefully to a no-op if `DATABASE_URL` is unset/unreachable — history is a nice-to-have, never a hard dependency for the core analyze pipeline.
- **`models.py`**: `classification`/`risk_category` are now `Literal[...]`-typed (real Pydantic validation, previously plain `str` with only a comment documenting the allowed values).
- **Nationwide legal knowledge base expansion**: `backend/knowledge_base.json` (6 entries, Central only) split into `backend/knowledge_base/*.json` per jurisdiction, expanded to **77 cited statute entries across 15 jurisdictions** (Central plus Delhi, Maharashtra, Haryana, Madhya Pradesh, Bihar, Telangana, Kerala, Punjab, Uttar Pradesh, Gujarat, Rajasthan, Tamil Nadu, Karnataka, West Bengal) via parallel-researched web sourcing — every entry carries a `source` citation, with honest confidence hedging where section-number precision is lower than a primary-source read. One research pass caught and corrected a widely-circulated but false claim (a "2-month Karnataka deposit cap" reported by several 2025-26 real-estate blogs, which direct review of the actual amendment bill text showed doesn't exist). `jurisdiction_guide.json` adds a correctly-categorized "which law applies to you" reference covering all 28 states + 8 union territories (distinct act / Model Tenancy Act adopted / general contract law / unable to verify), surfacing several Model Tenancy Act adopters beyond what was previously known (Assam, Uttarakhand, Arunachal Pradesh, J&K, Ladakh, plus 3 Article-240 union territories).
- **Frontend**: the jurisdiction dropdown (`frontend/src/app/analyze/page.tsx`) now lists every jurisdiction with real backend coverage instead of 3 hardcoded options, with a small info note showing which Act applies and its key caveat (e.g. Delhi's Rs. 3,500 rent-threshold limitation).
- **Evaluation suite**: `backend/eval/` adds a 38-case hand-labeled test set spanning all 15 covered jurisdictions and all three classifications, plus `run_eval.py` reporting retrieval hit-rate, classification agreement rate, and latency percentiles (p50/p95/p99) — a lightweight, re-runnable metric report with no extra LLM-judge cost.
- **Clause segmentation improvement**: `clause_segmenter.py` now also detects bullet/dash list items and ALL-CAPS section headers (previously only numbered/Section/Clause/Article markers).

### Verified this session
Ran the full 38-case eval set through the real hybrid-retrieval + reranking pipeline (embeddings, Chroma, BM25, RRF fusion, cross-encoder reranking — no mocks) against the complete 77-entry knowledge base: **37/38 = 97.4% retrieval hit-rate**, the expected statute landing as the #1 result in all but one deliberately ambiguous test clause. Also confirmed the app's full route surface (`/api/v1/health`, `/api/v1/history`, `/api/v1/history/{session_id}`, `/api/v1/analyze`) initializes without error, and that `Database` degrades gracefully with no `DATABASE_URL` set. Not yet run in this session: the LLM generation step itself (needs a real `GROQ_API_KEY`, not available in this environment) and live wall-clock timing versus the original 7-minute run — both pending a real deploy of this branch.

## Outstanding Features (Gap Analysis against ClauseGuard Final Report)
*The following system features are outlined in the Final Report but currently remain pending or partially implemented:*

### Pending Functional Requirements
- **Regex-based Structured Data Extraction (UC04)**: The system currently relies fully on the semantic RAG pipeline. The report specifies a parallel data extraction branch using regex to pull precise terms like rent, dates, and deposit values.
- **Export Analysis as PDF Report (UC08)**: The functionality allowing a user to download their parsed interactive risk report as a static PDF file is absent.
- ~~**Dynamic Jurisdiction Selection (UC02)**~~ — **Addressed in Session 6** (on the `arunav` branch, not yet merged to production): the dropdown now covers 15 jurisdictions with real, cited statute content instead of 3 hardcoded options, plus a 36-state/UT reference guide. Still needs to be merged to `master` before it's live.
- **Admin Panel / Knowledge Base Management (UC12)**: There is currently no dedicated web interface or secure admin route to seamlessly add, edit, or delete legal statutes directly into the ChromaDB vector database.
- **Email Registration Verification Flow (UC09)**: While Firebase mapping is established, the explicit backend verification process (requiring email tokens before confirming Registered User status) has yet to be fully integrated as specified in the Sequence Diagrams.
