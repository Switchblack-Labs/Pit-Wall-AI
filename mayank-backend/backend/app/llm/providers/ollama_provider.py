"""Local Ollama Granite provider.

Talks to a local Ollama server (default ``http://localhost:11434``) using its
native ``/api/generate`` endpoint. No API key is required; the only
prerequisite is a reachable Ollama server with a Granite model pulled, e.g.::

    ollama pull granite3.3:8b

Uses ``requests`` (already a project dependency) so no extra SDK is needed.
"""

from __future__ import annotations

from typing import Optional

from app.llm.base import GraniteProvider, LLMResult
from app.utils.logger import logger


class OllamaGraniteProvider(GraniteProvider):
    """Granite served by a local Ollama instance."""

    name = "ollama"

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        super().__init__(model=model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        if not self.base_url:
            return False
        try:
            import requests
        except ImportError:  # pragma: no cover - requests is a core dep
            return False
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2.0)
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001 - availability probe must not raise
            logger.debug("Ollama availability probe failed: %s", exc)
            return False

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        import requests

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        resp = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        return LLMResult(
            text=(data.get("response") or "").strip(),
            provider=self.name,
            model=self.model,
            raw=data,
        )
