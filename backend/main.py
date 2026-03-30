from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from typing import List

from backend.models import UploadResponse, AnalysisReport, ClauseAnalysis
from backend.ocr_service import OCRService
from backend.rag_service import RAGService
from backend.clause_segmenter import ClauseSegmenter
from backend.risk_calculator import RiskCalculator

app = FastAPI(title="Clause-Guard API", version="0.1.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
rag_service = RAGService()

@app.get("/")
async def root():
    return {"message": "Welcome to Clause-Guard API"}

@app.post("/api/v1/analyze", response_model=AnalysisReport)
async def analyze_document(file: UploadFile = File(...), jurisdiction: str = "Central"):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # 1. Save file temporarily
    session_id = str(uuid.uuid4())
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, f"{session_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        # 2. Extract Text (OCR fallback)
        raw_text = OCRService.extract_text_from_pdf(file_path)
        
        # 3. Segment into Clauses
        clauses_text = ClauseSegmenter.segment_text(raw_text)
        
        # 4. Analyze each clause with RAG + Ollama
        analyzed_clauses = []
        for text in clauses_text:
            analysis = rag_service.analyze_clause(text, jurisdiction)
            clause_obj = ClauseAnalysis(
                original_text=text,
                classification=analysis.get("classification", "FAIR"),
                explanation=analysis.get("explanation", "No explanation provided."),
                statute_cited=analysis.get("statute_cited")
            )
            analyzed_clauses.append(clause_obj.dict())
        
        # 5. Calculate Risk Score
        risk_data = RiskCalculator.calculate_score(analyzed_clauses)
        
        # 6. Build Final Report
        report = AnalysisReport(
            session_id=session_id,
            filename=file.filename,
            jurisdiction=jurisdiction,
            risk_score=risk_data["score"],
            risk_category=risk_data["category"],
            clauses=analyzed_clauses
        )
        
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up temp file if needed (optional for session history debugging)
        # os.remove(file_path)
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
