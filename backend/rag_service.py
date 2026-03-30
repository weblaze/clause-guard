import json
import os
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import logging


class RAGService:
    def __init__(self, db_dir: str = "chroma_db", model_name: str = "llama3"):
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.db_dir = db_dir

        # Standardize the base URL to use the robust OpenAI-compatible `/v1` endpoint
        # Example: https://ollama.com -> https://ollama.com/v1
        ollama_api_key = os.getenv("OLLAMA_API_KEY", "").replace("Bearer ", "").strip()
        safe_base_url = ollama_base_url.rstrip('/')
        if not safe_base_url.endswith('/v1'):
            if safe_base_url.endswith('/api'):
                safe_base_url = safe_base_url[:-4]
            safe_base_url = f"{safe_base_url}/v1"

        self.embeddings = OpenAIEmbeddings(
            openai_api_base=safe_base_url,
            openai_api_key=ollama_api_key or "sk-placeholder",
            model="all-minilm"
        )
        self.llm = ChatOpenAI(
            openai_api_base=safe_base_url,
            openai_api_key=ollama_api_key or "sk-placeholder",
            model=model_name
        )
        self.vector_store = None
        self.initialize_vector_store()

    def initialize_vector_store(self):
        """Initialize ChromaDB and load initial knowledge base if empty."""
        self.vector_store = Chroma(
            persist_directory=self.db_dir,
            embedding_function=self.embeddings
        )
        
        # Check if empty (simple check: if no documents or if it's new)
        # For simplicity in this MVP, we'll check if knowledge_base.json exists
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r") as f:
                kb_data = json.load(f)
                try:
                    self.add_statutes_to_db(kb_data)
                except Exception as e:
                    logging.error(f"Failed to embed initial knowledge base. Is your Ollama server running? Error: {e}")

    def add_statutes_to_db(self, statutes: List[Dict]):
        """Add legal statutes to the vector store with metadata."""
        texts = [s["text"] for s in statutes]
        metadatas = [
            {
                "id": s["id"],
                "title": s["title"],
                "jurisdiction": s["jurisdiction"],
                "category": s["category"],
                "source": s["source"]
            } for s in statutes
        ]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        self.vector_store.persist()

    def analyze_clause(self, clause_text: str, jurisdiction: str = "Central") -> Dict:
        """Analyze a specific lease clause using RAG + Ollama."""
        # Query ChromaDB for relevant statutes
        results = self.vector_store.similarity_search(
            clause_text, 
            k=3, 
            filter={"jurisdiction": jurisdiction}
        )
        
        context = "\n\n".join([r.page_content for r in results])
        
        # Construct prompt
        prompt_template = """
        You are a legal expert specialized in Indian Tenancy Laws.
        Analyze the following lease clause against the provided legal context.
        
        LEASE CLAUSE:
        {clause_text}
        
        RELEVANT INDIAN STATUTES/LAWS:
        {context}
        
        Task:
        1. Classify the clause as: FAIR, UNFAIR, or ILLEGAL.
        2. Provide a plain-English explanation for the classification.
        3. Cite the relevant statute if any.
        
        Response format (JSON only):
        {{
            "classification": "...",
            "explanation": "...",
            "statute_cited": "..."
        }}
        """
        
        prompt = prompt_template.format(clause_text=clause_text, context=context)
        response = self.llm.invoke(prompt)
        
        try:
            # Simple JSON parse attempt
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Invalid LLM response format", "raw": response}
        except Exception as e:
            return {"error": f"Parsing error: {str(e)}", "raw": response}
