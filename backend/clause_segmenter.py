import re
from typing import List

class ClauseSegmenter:
    @staticmethod
    def segment_text(raw_text: str) -> List[str]:
        """Segments raw lease text into individual clauses based on common numbering and section patterns."""
        # 1. CLEANING
        # Remove common headers/footers (e.g., "Page X of Y")
        text = re.sub(r'Page \d+ of \d+', '', raw_text)

        # Mark bullet/dash list items and ALL-CAPS section headers with a sentinel *before*
        # whitespace gets collapsed below, since collapsing newlines destroys the line-start
        # cues those patterns depend on.
        text = re.sub(r'(?m)^[ \t]*[•\-\*]\s+', '\x00', text)
        text = re.sub(r'(?m)^[ \t]*([A-Z][A-Z \t]{4,}[A-Z])[ \t]*$', lambda m: '\x00' + m.group(1), text)

        # Collapse multiple newlines/spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # 2. SEGMENTATION STRATEGY
        # We look for section headers like "1.", "Section 1", "Clause A", "Article I", etc.,
        # plus the sentinel-marked bullet/ALL-CAPS boundaries above.
        # This is a heuristic. We'll use split with regex.

        # Pattern: Numbered sections (1., 2.), word sections (Section 1:, Clause 2:), or
        # sentinel-marked bullet/header boundaries.
        patterns = [
            r'(?=\b\d+\s*[\.\)])',         # 1. 2. 1) 2)
            r'(?=\bSection\s+\d+[:\s])',   # Section 1:
            r'(?=\bClause\s+\d+[:\s])',    # Clause 1:
            r'(?=\bArticle\s+[IVX]+[:\s])', # Article I:
            r'(?=\x00)',                    # bullet/dash items and ALL-CAPS headers
        ]

        combined_pattern = "|".join(patterns)
        clauses = re.split(combined_pattern, text)

        # Clean up each clause (strip the sentinel marker, remove empty/whitespace)
        cleaned_clauses = [
            c.strip().lstrip('\x00').strip()
            for c in clauses
        ]
        cleaned_clauses = [c for c in cleaned_clauses if len(c) > 50]  # Ignore very short segments

        return cleaned_clauses

    @staticmethod
    def fuzzy_deduplicate(clauses: List[str], threshold: float = 0.9) -> List[str]:
        """Optionally remove nearly identical clauses if needed (e.g., from overlapping OCR)."""
        # Placeholder for future improvement if needed
        return clauses
