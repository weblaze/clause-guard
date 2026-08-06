import hashlib
from collections import OrderedDict
from typing import Optional

from backend.rag.llm_provider import ClauseAnalysisSchema


def _cache_key(clause_text: str, jurisdiction: str) -> str:
    normalized = clause_text.strip().lower() + "|" + jurisdiction
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class ClauseCache:
    """Exact-match cache keyed on (clause_text, jurisdiction). Skips the entire
    retrieve->generate cycle for a repeated/boilerplate clause seen earlier in the same
    running instance - common across lease templates sharing identical standard clauses.
    In-memory only: resets on redeploy/cold-start, same as everything else on Render's free
    tier. A persistent/shared cache (Redis, etc.) is a natural future upgrade, not needed here."""

    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._store: "OrderedDict[str, ClauseAnalysisSchema]" = OrderedDict()

    def get(self, clause_text: str, jurisdiction: str) -> Optional[ClauseAnalysisSchema]:
        key = _cache_key(clause_text, jurisdiction)
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, clause_text: str, jurisdiction: str, result: ClauseAnalysisSchema) -> None:
        key = _cache_key(clause_text, jurisdiction)
        self._store[key] = result
        self._store.move_to_end(key)
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)
