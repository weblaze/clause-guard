import asyncio
import os
from typing import Optional, Protocol

from groq import AsyncGroq
from groq import APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel


class ClauseAnalysisSchema(BaseModel):
    classification: str  # FAIR, UNFAIR, ILLEGAL
    explanation: str
    statute_cited: Optional[str] = None


CLAUSE_ANALYSIS_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "clause_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "classification": {"type": "string", "enum": ["FAIR", "UNFAIR", "ILLEGAL"]},
                "explanation": {"type": "string"},
                "statute_cited": {"type": ["string", "null"]},
            },
            "required": ["classification", "explanation", "statute_cited"],
            "additionalProperties": False,
        },
    },
}


class LLMProvider(Protocol):
    """Interface for a clause-classification backend. Only GroqProvider is implemented
    today, but keeping this as an interface rather than a hardcoded client is what lets a
    second provider be dropped in later without touching the RAG graph that calls it."""

    async def analyze(self, prompt: str) -> ClauseAnalysisSchema: ...


class GroqProvider:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.timeout_seconds = int(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(os.getenv("GROQ_MAX_RETRIES", "2"))

    async def analyze(self, prompt: str) -> ClauseAnalysisSchema:
        raw = await self._call_with_retry(prompt)
        return ClauseAnalysisSchema.model_validate_json(raw)

    async def _call_with_retry(self, prompt: str) -> str:
        delay = 1.0
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=CLAUSE_ANALYSIS_JSON_SCHEMA,
                    temperature=0.1,
                    max_tokens=400,
                    timeout=self.timeout_seconds,
                )
                return resp.choices[0].message.content
            except RateLimitError as e:
                last_err = e
            except (APIConnectionError, APIStatusError) as e:
                last_err = e
            if attempt < self.max_retries:
                await asyncio.sleep(delay)
                delay *= 2
        raise last_err
