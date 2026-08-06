import logging
import os

from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from backend.rag.cache import ClauseCache
from backend.rag.graph import CorrectiveRAGPipeline
from backend.rag.llm_provider import GroqProvider
from backend.rag.reranker import Reranker
from backend.rag.retrieval import HybridRetriever, load_knowledge_base

logger = logging.getLogger(__name__)

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")


def build_pipeline(db_dir: str = "chroma_db") -> CorrectiveRAGPipeline:
    """Wires together embeddings, vector store, hybrid retrieval, reranking, the Groq
    provider, and the caching layer into a single corrective-RAG pipeline. Kept separate
    from main.py so the HTTP layer stays focused purely on routing."""
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vector_store = Chroma(persist_directory=db_dir, embedding_function=embeddings)

    kb_data = load_knowledge_base(KB_DIR)
    if kb_data:
        try:
            vector_store.add_texts(
                texts=[s["text"] for s in kb_data],
                metadatas=[
                    {
                        "id": s["id"],
                        "title": s["title"],
                        "jurisdiction": s["jurisdiction"],
                        "category": s["category"],
                        "source": s["source"],
                    }
                    for s in kb_data
                ],
                ids=[s["id"] for s in kb_data],
            )
        except Exception as e:
            # Explicit IDs make this idempotent across restarts against a persisted Chroma
            # dir; a duplicate-ID error here just means the knowledge base is already
            # embedded from a prior run, which is fine.
            logger.info(f"Knowledge base embedding skipped/partial (likely already present): {e}")
    else:
        logger.warning(f"No knowledge base files found under {KB_DIR} - retrieval will return no context.")

    retriever = HybridRetriever(vector_store, kb_data)
    reranker = Reranker()
    llm = GroqProvider()
    cache = ClauseCache()

    return CorrectiveRAGPipeline(retriever, reranker, llm, cache)
