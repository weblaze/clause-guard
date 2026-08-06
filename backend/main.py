import asyncio
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import uvicorn

from backend.ocr_service import OCRService
from backend.clause_segmenter import ClauseSegmenter
from backend.risk_calculator import RiskCalculator
from backend.rag.setup import build_pipeline
from backend.db import Database
from backend.models import AnalysisReport, AnalysisRunOut, AnalysisRunSummaryOut, ClauseResultOut

GROQ_CONCURRENCY = int(os.environ.get("GROQ_CONCURRENCY", "4"))
CLAUSE_TIMEOUT_SECONDS = int(os.environ.get("CLAUSE_TIMEOUT_SECONDS", "20"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    yield


app = FastAPI(title="Clause-Guard API", version="0.2.0", lifespan=lifespan)

# CORS: allow local dev plus any Vercel deployment of this project by default.
_default_origins = ["http://localhost:3000"]
_extra_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_origin_regex=r"https://clause-guard.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Basic in-memory per-IP rate limiting for the analysis endpoint.
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 10
_request_log = defaultdict(list)


def _enforce_rate_limit(client_ip: str):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    recent = [t for t in _request_log[client_ip] if t > window_start]
    recent.append(now)
    _request_log[client_ip] = recent
    if len(recent) > RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again in a minute.")


# Initialize services
ocr_service = OCRService()
pipeline = build_pipeline()
db = Database()


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "engine": "Render Cloud", "llm_provider": "groq"}


@app.get("/api/v1/history", response_model=List[AnalysisRunSummaryOut])
async def get_history(limit: int = 20):
    runs = await db.list_recent_runs(limit=limit)
    return [
        AnalysisRunSummaryOut(
            session_id=r.session_id,
            filename=r.filename,
            jurisdiction=r.jurisdiction,
            risk_score=r.risk_score,
            risk_category=r.risk_category,
            created_at=r.created_at.isoformat(),
        )
        for r in runs
    ]


@app.get("/api/v1/history/{session_id}", response_model=AnalysisRunOut)
async def get_history_detail(session_id: str):
    run = await db.get_run(session_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return AnalysisRunOut(
        session_id=run.session_id,
        filename=run.filename,
        jurisdiction=run.jurisdiction,
        risk_score=run.risk_score,
        risk_category=run.risk_category,
        created_at=run.created_at.isoformat(),
        clauses=[
            ClauseResultOut(
                original_text=c.original_text,
                classification=c.classification,
                explanation=c.explanation,
                statute_cited=c.statute_cited,
                analysis_failed=c.analysis_failed,
            )
            for c in run.clauses
        ],
    )


@app.post("/api/v1/analyze", response_model=AnalysisReport)
async def analyze_document(request: Request, file: UploadFile = File(...), jurisdiction: str = "Central"):
    """Accepts a direct PDF upload and runs the full analysis pipeline."""
    _enforce_rate_limit(request.client.host if request.client else "unknown")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    session_id = str(uuid.uuid4())
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Security: Use deterministic ID for file path to prevent Path Traversal
    file_path = os.path.join(upload_dir, f"{session_id}.pdf")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        raw_text = await asyncio.to_thread(ocr_service.extract_text_from_file, file_path)
        return await _run_pipeline(raw_text, jurisdiction, session_id, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def _analyze_one_clause(t: str, jurisdiction: str, semaphore: asyncio.Semaphore) -> dict:
    failed = False
    async with semaphore:
        try:
            result = await asyncio.wait_for(
                pipeline.analyze_clause(t, jurisdiction), timeout=CLAUSE_TIMEOUT_SECONDS
            )
            classification, explanation, statute_cited = result.classification, result.explanation, result.statute_cited
        except Exception as e:
            classification = "UNFAIR"
            explanation = f"Automated analysis failed for this clause ({type(e).__name__}); flagged for manual review."
            statute_cited = None
            failed = True

    return {
        "original_text": t,
        "classification": classification,
        "explanation": explanation,
        "statute_cited": statute_cited,
        "analysis_failed": failed,
    }


async def _run_pipeline(text: str, jurisdiction: str, session_id: str, filename: str):
    # Segment into Clauses
    clauses_text = ClauseSegmenter.segment_text(text)

    # Analyze all clauses concurrently, bounded by GROQ_CONCURRENCY, each with its own timeout
    semaphore = asyncio.Semaphore(GROQ_CONCURRENCY)
    analyzed_clauses = list(
        await asyncio.gather(*[_analyze_one_clause(t, jurisdiction, semaphore) for t in clauses_text])
    )

    # Calculate Risk Score
    risk_data = RiskCalculator.calculate_score(analyzed_clauses)

    await db.save_run(
        session_id=session_id,
        filename=filename,
        jurisdiction=jurisdiction,
        risk_score=risk_data["score"],
        risk_category=risk_data["category"],
        clauses=analyzed_clauses,
    )

    return {
        "session_id": session_id,
        "filename": filename,
        "jurisdiction": jurisdiction,
        "risk_score": risk_data["score"],
        "risk_category": risk_data["category"],
        "clauses": analyzed_clauses,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
