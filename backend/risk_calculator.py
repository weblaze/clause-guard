from typing import List, Dict
from backend.models import ClauseAnalysis, AnalysisReport

class RiskCalculator:
    # Severity weights based on classification
    WEIGHTS = {
        "FAIR": 0,
        "UNFAIR": 10,
        "ILLEGAL": 30
    }

    @staticmethod
    def calculate_score(clauses: List[Dict]) -> Dict:
        """
        Calculates an aggregate risk score (0-100) based on weighted clause classifications.
        Returns the score and its category (LOW, MEDIUM, HIGH).
        """
        if not clauses:
            return {"score": 0, "category": "LOW"}
            
        total_weight = 0
        for clause in clauses:
            classification = clause.get("classification", "FAIR").upper()
            total_weight += RiskCalculator.WEIGHTS.get(classification, 0)
            clause["severity_weight"] = RiskCalculator.WEIGHTS.get(classification, 0)
            
        # Normalization: Max score capped at 100
        # If we have 3 illegal clauses (3*30=90) or 10 unfair (10*10=100), we hit the limit.
        score = min(100, total_weight)
        
        category = "LOW"
        if score >= 60:
            category = "HIGH"
        elif score >= 30:
            category = "MEDIUM"
            
        return {
            "score": score,
            "category": category
        }
