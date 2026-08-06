import time
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import uvicorn

from backend.ocr_service import OCRService
from backend.rag_service import RAGService
from backend.clause_segmenter import ClauseSegmenter
from backend.risk_calculator import RiskCalculator

app = FastAPI(title="Clause-Guard API", version="0.1.0")

# CORS: allow local dev plus any Vercel deployment of this project by default.
# Add extra allowed origins (e.g. a custom domain) via the ALLOWED_ORIGINS
# env var as a comma-separated list.
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

# Initialize Services
ocr_service = OCRService()
rag_service = RAGService()

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "engine": "Railway Cloud"}

@app.post("/api/v1/analyze")
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
        raw_text = ocr_service.extract_text_from_file(file_path)
        return await _run_pipeline(raw_text, jurisdiction, session_id, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def _run_pipeline(text: str, jurisdiction: str, session_id: str, filename: str):
    # Segment into Clauses
    clauses_text = ClauseSegmenter.segment_text(text)

    # Analyze each clause with RAG + Ollama
    analyzed_clauses = []
    for t in clauses_text:
        analysis = rag_service.analyze_clause(t, jurisdiction)
        analyzed_clauses.append({
            "original_text": t,
            "classification": analysis.get("classification", "FAIR"),
            "explanation": analysis.get("explanation", "No explanation."),
            "statute_cited": analysis.get("statute_cited")
        })

    # Calculate Risk Score
    risk_data = RiskCalculator.calculate_score(analyzed_clauses)

    return {
        "session_id": session_id,
        "filename": filename,
        "jurisdiction": jurisdiction,
        "risk_score": risk_data["score"],
        "risk_category": risk_data["category"],
        "clauses": analyzed_clauses
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
