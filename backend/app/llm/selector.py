"""Provider selection and runtime fallback.

:class:`AutoProviderSelector` is itself a :class:`GraniteProvider`, so callers
depend only on the base contract. It holds an ordered list of candidate
providers and, on each call, delegates to the first *available* one. If a
provider raises at generation time, the selector transparently falls back to
the next candidate, guaranteeing a result (the terminal candidate is always the
offline :class:`EchoProvider`).
"""

from __future__ import annotations

from typing import List, Optional

from app.llm.base import GraniteProvider, LLMResult
from app.llm.providers.echo import EchoProvider
from app.utils.logger import logger


class AutoProviderSelector(GraniteProvider):
    """Delegating provider that picks the first available candidate and
    falls back through the remaining candidates on error."""

    name = "auto"

    def __init__(self, candidates: List[GraniteProvider]) -> None:
        # Guarantee a terminal, always-available provider.
        if not any(isinstance(c, EchoProvider) for c in candidates):
            candidates = [*candidates, EchoProvider()]
        self._candidates = candidates
        # The "model" of the selector is whichever it would use first.
        active = self.active_provider()
        super().__init__(model=active.model)

    def active_provider(self) -> GraniteProvider:
        """Return the first candidate that reports availability."""
        for candidate in self._candidates:
            try:
                if candidate.is_available():
                    return candidate
            except Exception as exc:  # noqa: BLE001 - probe must not raise
                logger.warning(
                    "Availability check failed for %s: %s", candidate.name, exc
                )
        # EchoProvider is always available, so this is effectively unreachable.
        return self._candidates[-1]

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        last_error: Optional[Exception] = None
        for candidate in self._candidates:
            try:
                if not candidate.is_available():
                    continue
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping %s (probe error): %s", candidate.name, exc)
                continue
            try:
                return candidate.generate(
                    prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except Exception as exc:  # noqa: BLE001 - fall back to next provider
                last_error = exc
                logger.warning(
                    "Provider %s failed (%s); falling back.", candidate.name, exc
                )
                continue

        # Should never happen: EchoProvider cannot fail. Surface defensively.
        raise RuntimeError(
            f"All LLM providers failed; last error: {last_error}"
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        names = ", ".join(c.name for c in self._candidates)
        return f"<AutoProviderSelector [{names}]>"
