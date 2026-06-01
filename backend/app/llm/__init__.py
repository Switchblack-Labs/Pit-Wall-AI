"""LLM provider abstraction for Pit Wall AI.

This package is the single inference seam for the backend. All reasoning
(FIA RAG answers, strategy explanations, orchestration workflows) goes through
:class:`~app.llm.base.GraniteProvider`. Concrete providers (watsonx, Replicate,
Ollama) are swappable via environment variables, with a deterministic offline
``echo`` provider as the always-available fallback so CI and reviewers can run
the full stack with no network access or cloud credentials.
"""

from app.llm.base import GraniteProvider, LLMResult
from app.llm.factory import get_llm_provider, reset_llm_provider

__all__ = [
    "GraniteProvider",
    "LLMResult",
    "get_llm_provider",
    "reset_llm_provider",
]
