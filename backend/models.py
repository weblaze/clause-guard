from pydantic import BaseModel, Field
from typing import List, Optional

class ClauseAnalysis(BaseModel):
    original_text: str
    cleaned_text: Optional[str] = None
    classification: str # FAIR, UNFAIR, ILLEGAL
    explanation: str
    statute_cited: Optional[str] = None
    severity_weight: int = 0

class AnalysisReport(BaseModel):
    session_id: str
    filename: str
    jurisdiction: str
    risk_score: int
    risk_category: str # LOW, MEDIUM, HIGH
    clauses: List[ClauseAnalysis]
    summary: Optional[str] = None

class UploadResponse(BaseModel):
    filename: str
    jurisdiction: str
    session_id: str
    status: str
