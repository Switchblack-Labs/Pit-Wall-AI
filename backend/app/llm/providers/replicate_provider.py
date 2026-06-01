"""Replicate-hosted IBM Granite provider.

Calls Granite models published on Replicate (e.g.
``ibm-granite/granite-3.3-8b-instruct``) using the ``replicate`` SDK, which is
already a project dependency. Requires ``REPLICATE_API_TOKEN`` in the
environment.
"""

from __future__ import annotations

from typing import Optional

from app.llm.base import GraniteProvider, LLMResult
from app.utils.logger import logger


class ReplicateGraniteProvider(GraniteProvider):
    """Granite served by Replicate."""

    name = "replicate"

    def __init__(self, *, model: str, api_token: str) -> None:
        super().__init__(model=model)
        self.api_token = api_token

    def is_available(self) -> bool:
        if not self.api_token:
            return False
        try:
            import replicate
        except ImportError:
            logger.warning(
                "replicate selected but the replicate package is not "
                "installed; skipping this provider."
            )
            return False
        return True

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        import replicate

        client = replicate.Client(api_token=self.api_token)
        model_input = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": max(temperature, 0.01),
        }
        if system:
            model_input["system_prompt"] = system

        output = client.run(self.model, input=model_input)
        if isinstance(output, (list, tuple)):
            text = "".join(str(chunk) for chunk in output)
        elif isinstance(output, str):
            text = output
        else:
            text = "".join(str(chunk) for chunk in output)

        return LLMResult(
            text=text.strip(),
            provider=self.name,
            model=self.model,
            raw=None,
        )
