from typing import List, Literal, Optional

from pydantic import BaseModel


class ClauseAnalysis(BaseModel):
    original_text: str
    cleaned_text: Optional[str] = None
    classification: Literal["FAIR", "UNFAIR", "ILLEGAL"]
    explanation: str
    statute_cited: Optional[str] = None
    severity_weight: int = 0
    analysis_failed: bool = False


class AnalysisReport(BaseModel):
    session_id: str
    filename: str
    jurisdiction: str
    risk_score: int
    risk_category: Literal["LOW", "MEDIUM", "HIGH"]
    clauses: List[ClauseAnalysis]
    summary: Optional[str] = None


class UploadResponse(BaseModel):
    filename: str
    jurisdiction: str
    session_id: str
    status: str


class ClauseResultOut(BaseModel):
    original_text: str
    classification: Literal["FAIR", "UNFAIR", "ILLEGAL"]
    explanation: str
    statute_cited: Optional[str] = None
    analysis_failed: bool = False

    class Config:
        from_attributes = True


class AnalysisRunOut(BaseModel):
    session_id: str
    filename: str
    jurisdiction: str
    risk_score: int
    risk_category: Literal["LOW", "MEDIUM", "HIGH"]
    created_at: str
    clauses: List[ClauseResultOut] = []

    class Config:
        from_attributes = True


class AnalysisRunSummaryOut(BaseModel):
    session_id: str
    filename: str
    jurisdiction: str
    risk_score: int
    risk_category: Literal["LOW", "MEDIUM", "HIGH"]
    created_at: str

    class Config:
        from_attributes = True
