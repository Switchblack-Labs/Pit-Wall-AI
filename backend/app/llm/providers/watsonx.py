"""IBM watsonx.ai Granite provider.

Uses the official ``ibm-watsonx-ai`` SDK. Credentials come from the environment
via :class:`app.config.Settings`:

* ``WATSONX_API_KEY``
* ``WATSONX_PROJECT_ID``
* ``WATSONX_URL`` (region endpoint, e.g. ``https://us-south.ml.cloud.ibm.com``)

The SDK is imported lazily so the backend does not require ``ibm-watsonx-ai``
to be installed unless this provider is actually selected.
"""

from __future__ import annotations

from typing import Optional

from app.llm.base import GraniteProvider, LLMResult
from app.utils.logger import logger


class WatsonXProvider(GraniteProvider):
    """Granite served by IBM watsonx.ai."""

    name = "watsonx"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        project_id: str,
        url: str,
    ) -> None:
        super().__init__(model=model)
        self.api_key = api_key
        self.project_id = project_id
        self.url = url
        self._client = None

    def is_available(self) -> bool:
        if not (self.api_key and self.project_id and self.url):
            return False
        try:
            import ibm_watsonx_ai  # noqa: F401
        except ImportError:
            logger.warning(
                "watsonx selected but ibm-watsonx-ai is not installed; "
                "skipping this provider."
            )
            return False
        return True

    def _get_model(self):
        if self._client is not None:
            return self._client

        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(url=self.url, api_key=self.api_key)
        self._client = ModelInference(
            model_id=self.model,
            credentials=credentials,
            project_id=self.project_id,
        )
        return self._client

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        model = self._get_model()
        full_prompt = f"{system.strip()}\n\n{prompt}" if system else prompt

        params = {
            "decoding_method": "greedy" if temperature <= 0 else "sample",
            "max_new_tokens": max_tokens,
            "temperature": max(temperature, 0.01),
        }
        resp = model.generate_text(prompt=full_prompt, params=params, raw_response=True)

        # ibm-watsonx-ai returns a dict with results[0]["generated_text"].
        text = ""
        if isinstance(resp, dict):
            results = resp.get("results") or []
            if results:
                text = results[0].get("generated_text", "")
        else:  # pragma: no cover - SDK returned plain string
            text = str(resp)

        return LLMResult(
            text=text.strip(),
            provider=self.name,
            model=self.model,
            raw=resp if isinstance(resp, dict) else None,
        )
