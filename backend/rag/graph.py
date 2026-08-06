import logging
from typing import Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from backend.rag.cache import ClauseCache
from backend.rag.llm_provider import ClauseAnalysisSchema, LLMProvider
from backend.rag.reranker import Reranker
from backend.rag.retrieval import HybridRetriever

PROMPT_TEMPLATE = """You are a legal expert specialized in Indian Tenancy Laws.
Analyze the following lease clause against the provided legal context.

LEASE CLAUSE:
{clause_text}

RELEVANT INDIAN STATUTES/LAWS:
{context}

Classify the clause as FAIR, UNFAIR, or ILLEGAL, give a one-to-two sentence plain-English
explanation, and cite the relevant statute if any. Only cite a statute that literally
appears in the context above; if none of the context is directly relevant, set
statute_cited to null."""


class ClauseState(TypedDict, total=False):
    clause_text: str
    jurisdiction: str
    candidates: List[Dict]
    rewritten: bool
    regenerated: bool
    result: ClauseAnalysisSchema


def _build_context(candidates: List[Dict]) -> str:
    return "\n\n".join(d["text"] for d in candidates) or "No directly relevant statute found."


def _citation_matches(cited: Optional[str], candidates: List[Dict]) -> bool:
    if not cited or not cited.strip():
        return True  # nothing cited -> nothing to contradict
    cited_lower = cited.strip().lower()
    for c in candidates:
        title = c.get("title", "").lower()
        source = c.get("source", "").lower()
        if title and (title in cited_lower or cited_lower in title):
            return True
        if source and (source in cited_lower or cited_lower in source):
            return True
    return False


class CorrectiveRAGPipeline:
    """A bounded, corrective-RAG-style cycle built on LangGraph:

        retrieve --(no relevant candidates?)--> rewrite --> generate
              \\--(candidates found)--------------------------/
                                                                |
                                                                v
                                              generate --(citation not grounded?)--> regenerate --> END
                                                    \\--(grounded / no citation)-------------------> END

    Both loop-back paths are hard-bounded to a single retry each (rewritten/regenerated
    flags), so a stuck or ambiguous clause can never spin forever - this composes with the
    caller's own per-clause timeout in main.py as a second, independent safety net.

    Grading and self-checking are deliberately cheap heuristics (candidate-count and
    string-containment checks), not a second LLM judgment call - a "real" Self-RAG/CRAG setup
    often re-invokes the LLM to grade itself, but that doubles the per-clause LLM cost and
    directly fights the speed goal this pipeline exists to fix.
    """

    def __init__(self, retriever: HybridRetriever, reranker: Reranker, llm: LLMProvider, cache: ClauseCache):
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.cache = cache
        self._graph = self._build()

    def _build(self):
        graph = StateGraph(ClauseState)

        async def retrieve_node(state: ClauseState) -> Dict:
            candidates = await self.retriever.retrieve(state["clause_text"], state["jurisdiction"])
            candidates = await self.reranker.rerank(state["clause_text"], candidates)
            return {"candidates": candidates}

        async def rewrite_node(state: ClauseState) -> Dict:
            broadened_query = f"{state['clause_text']} tenant landlord rent lease rights obligations"
            candidates = await self.retriever.retrieve(broadened_query, state["jurisdiction"])
            candidates = await self.reranker.rerank(state["clause_text"], candidates)
            return {"candidates": candidates, "rewritten": True}

        async def generate_node(state: ClauseState) -> Dict:
            prompt = PROMPT_TEMPLATE.format(
                clause_text=state["clause_text"], context=_build_context(state["candidates"])
            )
            result = await self.llm.analyze(prompt)
            return {"result": result}

        async def regenerate_node(state: ClauseState) -> Dict:
            correction = (
                "\n\nNOTE: Your previous answer cited a statute that does not appear in the "
                "context above. Only cite a statute if it literally appears in the context; "
                "otherwise set statute_cited to null."
            )
            prompt = (
                PROMPT_TEMPLATE.format(
                    clause_text=state["clause_text"], context=_build_context(state["candidates"])
                )
                + correction
            )
            result = await self.llm.analyze(prompt)
            return {"result": result, "regenerated": True}

        def route_after_retrieve(state: ClauseState) -> str:
            if not state["candidates"] and not state.get("rewritten"):
                return "rewrite"
            return "generate"

        def route_after_generate(state: ClauseState) -> str:
            result = state["result"]
            if state.get("regenerated"):
                return "end"
            if _citation_matches(result.statute_cited, state["candidates"]):
                return "end"
            return "regenerate"

        graph.add_node("retrieve", retrieve_node)
        graph.add_node("rewrite", rewrite_node)
        graph.add_node("generate", generate_node)
        graph.add_node("regenerate", regenerate_node)

        graph.set_entry_point("retrieve")
        graph.add_conditional_edges("retrieve", route_after_retrieve, {"rewrite": "rewrite", "generate": "generate"})
        graph.add_edge("rewrite", "generate")
        graph.add_conditional_edges("generate", route_after_generate, {"regenerate": "regenerate", "end": END})
        graph.add_edge("regenerate", END)

        return graph.compile()

    async def analyze_clause(self, clause_text: str, jurisdiction: str) -> ClauseAnalysisSchema:
        cached = self.cache.get(clause_text, jurisdiction)
        if cached is not None:
            return cached

        final_state = await self._graph.ainvoke({"clause_text": clause_text, "jurisdiction": jurisdiction})
        result = final_state["result"]

        if not result.statute_cited and final_state["candidates"]:
            result.statute_cited = final_state["candidates"][0].get("source") or final_state["candidates"][0].get("title")

        self.cache.set(clause_text, jurisdiction, result)
        return result
