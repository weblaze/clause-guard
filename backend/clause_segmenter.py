import re
from typing import List

class ClauseSegmenter:
    @staticmethod
    def segment_text(raw_text: str) -> List[str]:
        """Segments raw lease text into individual clauses based on common numbering and section patterns."""
        # 1. CLEANING
        # Remove common headers/footers (e.g., "Page X of Y")
        text = re.sub(r'Page \d+ of \d+', '', raw_text)
        # Collapse multiple newlines/spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 2. SEGMENTATION STRATEGY
        # We look for section headers like "1.", "Section 1", "Clause A", "Article I", etc.
        # This is a heuristic. We'll use split with regex.
        
        # Pattern: Numbered sections (1., 2.), or word sections (Section 1:, Clause 2:)
        patterns = [
            r'(?=\b\d+\s*[\.\)])',         # 1. 2. 1) 2)
            r'(?=\bSection\s+\d+[:\s])',   # Section 1:
            r'(?=\bClause\s+\d+[:\s])',    # Clause 1:
            r'(?=\bArticle\s+[IVX]+[:\s])', # Article I:
        ]
        
        combined_pattern = "|".join(patterns)
        clauses = re.split(combined_pattern, text)
        
        # Clean up each clause (remove empty strings and whitespace)
        cleaned_clauses = [c.strip() for c in clauses if len(c.strip()) > 50] # Ignore very short segments
        
        return cleaned_clauses

    @staticmethod
    def fuzzy_deduplicate(clauses: List[str], threshold: float = 0.9) -> List[str]:
        """Optionally remove nearly identical clauses if needed (e.g., from overlapping OCR)."""
        # Placeholder for future improvement if needed
        return clauses
