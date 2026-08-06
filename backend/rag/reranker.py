import asyncio
import os
from typing import Dict, List


class Reranker:
    """Local, free, CPU-based cross-encoder reranking via FastEmbed's TextCrossEncoder.
    Retrieval returns a wide candidate pool (~15-20 docs); this narrows it to the few most
    relevant before they're spent as LLM prompt context. RERANK_ENABLED is an escape hatch -
    Render's free tier is 512MB RAM, and this is a second local ONNX model alongside the
    embedder, so if that combination doesn't fit, disabling this still leaves a working
    pipeline (just ordered by RRF fusion alone instead of reranked)."""

    def __init__(self):
        self.enabled = os.getenv("RERANK_ENABLED", "true").lower() == "true"
        self.top_k = int(os.getenv("RERANK_TOP_K", "4"))
        self.model = None
        if self.enabled:
            from fastembed.rerank.cross_encoder import TextCrossEncoder

            model_name = os.getenv("RERANK_MODEL", "Xenova/ms-marco-MiniLM-L-6-v2")
            self.model = TextCrossEncoder(model_name=model_name)

    async def rerank(self, clause_text: str, candidates: List[Dict]) -> List[Dict]:
        if not candidates:
            return []
        if not self.enabled or self.model is None:
            return candidates[: self.top_k]
        return await asyncio.to_thread(self._rerank_sync, clause_text, candidates)

    def _rerank_sync(self, clause_text: str, candidates: List[Dict]) -> List[Dict]:
        docs = [c["text"] for c in candidates]
        scores = list(self.model.rerank(clause_text, docs))
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return [doc for doc, _ in ranked[: self.top_k]]
