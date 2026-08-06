import json
import os
import re
from pathlib import Path
from typing import Dict, List

from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi

RRF_K = 60


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def load_knowledge_base(kb_dir: str) -> List[Dict]:
    """Load every *.json file in knowledge_base/ into a single flat list of statute entries."""
    entries: List[Dict] = []
    kb_path = Path(kb_dir)
    if not kb_path.exists():
        return entries
    for file_path in sorted(kb_path.glob("*.json")):
        if file_path.name == "jurisdiction_guide.json":
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            entries.extend(json.load(f))
    return entries


class HybridRetriever:
    """Vector search (Chroma/FastEmbed) + BM25 keyword search, fused via Reciprocal Rank
    Fusion. Retrieval is strictly scoped to the requested jurisdiction - no cross-jurisdiction
    fallback, since every supported jurisdiction now has real, dedicated statute content."""

    def __init__(self, vector_store: Chroma, kb_data: List[Dict]):
        self.vector_store = vector_store
        self.kb_data = kb_data
        self.id_to_doc = {s["id"]: s for s in kb_data}
        self.bm25_index = BM25Okapi([_tokenize(s["text"]) for s in kb_data]) if kb_data else None
        self.available_jurisdictions = {s["jurisdiction"] for s in kb_data}
        self.retrieve_k = int(os.getenv("HYBRID_RETRIEVE_K", "15"))

    def has_dedicated_jurisdiction(self, jurisdiction: str) -> bool:
        return jurisdiction in self.available_jurisdictions

    async def retrieve(self, clause_text: str, jurisdiction: str) -> List[Dict]:
        if not self.kb_data:
            return []

        vector_hits = await self.vector_store.asimilarity_search(
            clause_text, k=self.retrieve_k, filter={"jurisdiction": jurisdiction}
        )
        vector_ids = [h.metadata["id"] for h in vector_hits if h.metadata.get("id") in self.id_to_doc]

        allowed_ids = {s["id"] for s in self.kb_data if s["jurisdiction"] == jurisdiction}
        bm25_ids: List[str] = []
        if self.bm25_index is not None and allowed_ids:
            scores = self.bm25_index.get_scores(_tokenize(clause_text))
            ranked = sorted(
                [(s["id"], sc) for s, sc in zip(self.kb_data, scores) if s["id"] in allowed_ids],
                key=lambda pair: pair[1],
                reverse=True,
            )[: self.retrieve_k]
            bm25_ids = [doc_id for doc_id, _ in ranked]

        rrf_scores: Dict[str, float] = {}
        for rank, doc_id in enumerate(vector_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        for rank, doc_id in enumerate(bm25_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)

        fused_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
        return [self.id_to_doc[i] for i in fused_ids if i in self.id_to_doc]
