"""Factory for constructing the configured LLM provider.

``get_llm_provider()`` returns a cached singleton built from
:class:`app.config.Settings`:

* ``LLM_PROVIDER=auto`` (default) -> an :class:`AutoProviderSelector` over the
  candidates listed in ``LLM_FALLBACK_ORDER``.
* ``LLM_PROVIDER=<name>`` -> that single provider, still wrapped so that an
  unavailable explicit provider degrades to ``echo`` instead of crashing.

The returned object always satisfies the :class:`GraniteProvider` contract, so
the rest of the backend depends only on the abstraction.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from app.config import Settings, get_settings
from app.llm.base import GraniteProvider
from app.llm.providers.echo import EchoProvider
from app.llm.providers.ollama_provider import OllamaGraniteProvider
from app.llm.providers.replicate_provider import ReplicateGraniteProvider
from app.llm.providers.watsonx import WatsonXProvider
from app.llm.selector import AutoProviderSelector
from app.utils.logger import logger

_PROVIDER_SINGLETON: Optional[GraniteProvider] = None


def _build_provider(name: str, settings: Settings) -> Optional[GraniteProvider]:
    """Construct a single provider by name, or ``None`` if name is unknown."""
    name = name.strip().lower()
    if name == "watsonx":
        return WatsonXProvider(
            model=settings.WATSONX_MODEL,
            api_key=settings.WATSONX_API_KEY,
            project_id=settings.WATSONX_PROJECT_ID,
            url=settings.WATSONX_URL,
        )
    if name == "replicate":
        return ReplicateGraniteProvider(
            model=settings.REPLICATE_MODEL,
            # Accept either the dedicated token or the legacy GRANITE_API_KEY.
            api_token=settings.REPLICATE_API_TOKEN or settings.GRANITE_API_KEY,
        )
    if name == "ollama":
        return OllamaGraniteProvider(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
    if name == "echo":
        return EchoProvider()
    return None


def _candidate_order(settings: Settings) -> List[str]:
    order = [p.strip().lower() for p in settings.LLM_FALLBACK_ORDER.split(",")]
    order = [p for p in order if p]
    if "echo" not in order:
        order.append("echo")
    return order


def build_provider_from_settings(settings: Settings) -> GraniteProvider:
    """Build (without caching) the provider implied by ``settings``."""
    selected = (settings.LLM_PROVIDER or "auto").strip().lower()

    if selected != "auto":
        provider = _build_provider(selected, settings)
        if provider is None:
            logger.warning(
                "Unknown LLM_PROVIDER=%r; falling back to auto-selection.",
                selected,
            )
        else:
            # Wrap the explicit choice so an unavailable provider degrades to
            # echo rather than erroring at request time.
            return AutoProviderSelector([provider, EchoProvider()])

    candidates: List[GraniteProvider] = []
    seen: Dict[str, bool] = {}
    for pname in _candidate_order(settings):
        if pname in seen:
            continue
        seen[pname] = True
        provider = _build_provider(pname, settings)
        if provider is not None:
            candidates.append(provider)

    selector = AutoProviderSelector(candidates)
    logger.info(
        "LLM provider initialised: active=%s candidates=%r",
        selector.active_provider().name,
        [c.name for c in candidates],
    )
    return selector


def get_llm_provider() -> GraniteProvider:
    """Return the cached, process-wide LLM provider singleton."""
    global _PROVIDER_SINGLETON
    if _PROVIDER_SINGLETON is None:
        _PROVIDER_SINGLETON = build_provider_from_settings(get_settings())
    return _PROVIDER_SINGLETON


def reset_llm_provider() -> None:
    """Clear the cached singleton (used by tests after changing env)."""
    global _PROVIDER_SINGLETON
    _PROVIDER_SINGLETON = None
