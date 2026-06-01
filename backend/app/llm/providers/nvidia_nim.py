from __future__ import annotations

from typing import Optional

import requests

from app.llm.base import GraniteProvider, LLMResult
from app.utils.logger import logger


class NvidiaNimProvider(GraniteProvider):
    name = "nvidia"

    def __init__(self, *, model: str, api_key: str, base_url: str) -> None:
        super().__init__(model=model)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def is_available(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LLMResult:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        try:
            text = payload["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("Unexpected NVIDIA NIM response shape: %s", payload)
            raise RuntimeError("Unexpected NVIDIA NIM response shape") from exc

        return LLMResult(
            text=str(text).strip(),
            provider=self.name,
            model=self.model,
            raw=payload,
        )
