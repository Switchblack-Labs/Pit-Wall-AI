"""Concrete LLM providers.

Each provider lazily imports its SDK so that importing this package never
requires every backend's dependencies to be installed. Missing prerequisites
surface as ``is_available() == False`` rather than import errors.
"""

from app.llm.providers.echo import EchoProvider
from app.llm.providers.ollama_provider import OllamaGraniteProvider
from app.llm.providers.replicate_provider import ReplicateGraniteProvider
from app.llm.providers.watsonx import WatsonXProvider

__all__ = [
    "EchoProvider",
    "OllamaGraniteProvider",
    "ReplicateGraniteProvider",
    "WatsonXProvider",
]
