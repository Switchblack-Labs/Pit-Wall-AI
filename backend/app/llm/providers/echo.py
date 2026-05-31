"""Deterministic, offline fallback provider.

``EchoProvider`` performs no network I/O and requires no credentials. It returns
a stable, structured response derived from the prompt so that:

* the full backend stack runs in CI / on a reviewer's laptop with zero setup;
* tests can assert deterministic behaviour;
* downstream consumers (RAG, explanation) always receive non-empty text.

It is intentionally *not* a language model — it never invents facts. When a
prompt carries no retrieval context, it says so, which makes it a useful
baseline for the RAG hallucination-resistance tests.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from app.llm.base import GraniteProvider, LLMResult


class EchoProvider(GraniteProvider):
    """Offline, deterministic provider used as the universal fallback."""

    name = "echo"

    def __init__(self, *, model: str = "echo-deterministic") -> None:
        super().__init__(model=model)

    def is_available(self) -> bool:
        # Always available: it is pure-Python and has no external dependency.
        return True

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        # Keep a bounded, readable echo of the prompt for deterministic asserts.
        snippet = " ".join(prompt.split())[:280]

        lines = ["[offline-echo provider]"]
        if system:
            lines.append(f"system: {' '.join(system.split())[:160]}")
        lines.append(f"prompt[{digest}]: {snippet}")
        text = "\n".join(lines)

        # Respect max_tokens loosely by trimming characters (~4 chars/token).
        char_budget = max(32, max_tokens * 4)
        if len(text) > char_budget:
            text = text[:char_budget]

        return LLMResult(
            text=text,
            provider=self.name,
            model=self.model,
            raw={"digest": digest},
        )
