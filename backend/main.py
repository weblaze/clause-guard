from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import uvicorn
from typing import List, Optional

from backend.ocr_service import OCRService
from backend.rag_service import RAGService
from backend.clause_segmenter import ClauseSegmenter
from backend.risk_calculator import RiskCalculator

app = FastAPI(title="Clause-Guard API", version="0.1.0")

# Enable CORS for Next.js frontend (Local & Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
ocr_service = OCRService()
rag_service = RAGService()

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "engine": "Railway Cloud"}

@app.post("/api/v1/analyze")
async def analyze_document(file: UploadFile = File(...), jurisdiction: str = "Central"):
    """Legacy local upload support."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    session_id = str(uuid.uuid4())
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, f"{session_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        # Use existing OCR logic (local file) - Note: Railway should use URL variant for scale
        return await _process_analysis(ocr_service.extract_text_from_url, file_path, jurisdiction, session_id, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/analyze-url")
async def analyze_url(file_url: str = Body(..., embed=True), jurisdiction: str = "Central"):
    """Cloud-native Supabase integration."""
    session_id = str(uuid.uuid4())
    try:
        raw_text = ocr_service.extract_text_from_url(file_url)
        return await _run_pipeline(raw_text, jurisdiction, session_id, "Supabase Cloud File")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
