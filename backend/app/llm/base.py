"""Base classes for the Granite/LLM provider abstraction."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMResult:
    """Normalized result returned by every provider.

    Attributes:
        text: The generated text.
        provider: Name of the provider that produced the result (e.g. ``"watsonx"``).
        model: Model identifier used for the generation.
        raw: Optional provider-specific raw payload, for debugging.
    """

    text: str
    provider: str
    model: str
    raw: Optional[dict] = field(default=None, repr=False)


class GraniteProvider(abc.ABC):
    """Abstract base class for all LLM providers.

    Concrete subclasses implement :meth:`generate` (synchronous). An async
    convenience wrapper :meth:`agenerate` is provided by the base class and
    offloads the sync call to a thread so it never blocks the event loop.

    The name "Granite" reflects the project's primary model family; providers
    may serve any model, which keeps the architecture swappable.
    """

    name: str = "base"

    def __init__(self, *, model: str) -> None:
        self.model = model

    @abc.abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        """Generate a completion for ``prompt``.

        Args:
            prompt: The user prompt / question.
            system: Optional system instruction steering behaviour.
            max_tokens: Upper bound on generated tokens.
            temperature: Sampling temperature; lower is more deterministic.

        Returns:
            A populated :class:`LLMResult`.

        Raises:
            Exception: Providers may raise on network/credential errors. The
                :class:`~app.llm.selector.AutoProviderSelector` is responsible
                for catching these and falling back.
        """

    async def agenerate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        """Async wrapper around :meth:`generate`.

        Runs the (potentially blocking) sync call in a worker thread so callers
        on the FastAPI event loop are never blocked.
        """
        import anyio

        return await anyio.to_thread.run_sync(
            lambda: self.generate(
                prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Return ``True`` if this provider has what it needs to run.

        Implementations should check for required credentials / reachable
        endpoints and import their SDK lazily, returning ``False`` (never
        raising) when prerequisites are missing.
        """

    def __repr__(self) -> str:
        return f"<{type(self).__name__} model={self.model!r}>"
