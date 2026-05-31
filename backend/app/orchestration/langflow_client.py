"""Optional LangFlow server client.

When ``LANGFLOW_URL`` is configured, :class:`LangFlowClient` can POST to a
running LangFlow server to execute a deployed flow. It is intentionally
best-effort: ``is_enabled()`` reports whether a server is configured, and
:meth:`run_flow` returns ``None`` on any failure so that callers transparently
fall back to the in-process Python pipeline.

The backend never hard-depends on LangFlow: this module imports only
``requests`` (already a dependency) and never raises at import time.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from app.config import get_settings
from app.utils.logger import logger


class LangFlowClient:
    """Thin, fault-tolerant client for a LangFlow server."""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout

    def is_enabled(self) -> bool:
        """True only when a LangFlow server URL is configured."""
        return bool(self.base_url)

    def run_flow(
        self,
        flow_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Execute a deployed flow by id/endpoint.

        Returns the parsed JSON response, or ``None`` if LangFlow is not
        configured or the call fails (caller should fall back in-process).
        """
        if not self.is_enabled():
            return None

        try:
            import requests
        except ImportError:  # pragma: no cover - requests is a core dep
            return None

        url = f"{self.base_url}/api/v1/run/{flow_id}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - degrade to in-process pipeline
            logger.warning(
                "LangFlow run failed for flow %s (%s); falling back in-process.",
                flow_id,
                exc,
            )
            return None


@lru_cache(maxsize=1)
def get_langflow_client() -> LangFlowClient:
    """Return a cached LangFlow client built from settings."""
    settings = get_settings()
    return LangFlowClient(
        base_url=settings.LANGFLOW_URL,
        api_key=settings.LANGFLOW_API_KEY,
    )
