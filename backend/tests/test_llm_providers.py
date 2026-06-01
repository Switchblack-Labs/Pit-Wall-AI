"""Tests for the Granite LLM provider abstraction and auto-selector."""

from app.llm.base import GraniteProvider, LLMResult
from app.llm.providers.echo import EchoProvider
from app.llm.selector import AutoProviderSelector


def test_echo_provider_is_always_available_and_deterministic():
    p = EchoProvider()
    assert p.is_available() is True
    r1 = p.generate("hello world", system="be brief")
    r2 = p.generate("hello world", system="be brief")
    assert isinstance(r1, LLMResult)
    assert r1.provider == "echo"
    assert r1.text == r2.text


class _BoomProvider(GraniteProvider):
    name = "boom"

    def __init__(self):
        super().__init__(model="boom")

    def is_available(self):
        return True

    def generate(self, prompt, *, system=None, max_tokens=512, temperature=0.2):
        raise RuntimeError("provider exploded")


class _UnavailableProvider(GraniteProvider):
    name = "nope"

    def __init__(self):
        super().__init__(model="nope")

    def is_available(self):
        return False

    def generate(self, prompt, *, system=None, max_tokens=512, temperature=0.2):
        raise AssertionError("should never be called")


def test_selector_appends_terminal_echo():
    sel = AutoProviderSelector([_UnavailableProvider()])
    assert sel.is_available() is True
    assert sel.active_provider().name == "echo"


def test_selector_skips_unavailable_and_uses_next():
    sel = AutoProviderSelector([_UnavailableProvider(), EchoProvider()])
    assert sel.active_provider().name == "echo"
    result = sel.generate("q")
    assert result.provider == "echo"


def test_selector_falls_back_on_generation_error():
    sel = AutoProviderSelector([_BoomProvider(), EchoProvider()])
    result = sel.generate("q")
    assert result.provider == "echo"


def test_factory_explicit_unknown_provider_degrades_to_echo():
    from app.config import Settings
    from app.llm.factory import build_provider_from_settings

    settings = Settings(LLM_PROVIDER="does-not-exist")
    provider = build_provider_from_settings(settings)
    assert provider.generate("q").provider == "echo"


def test_factory_auto_with_no_creds_selects_echo():
    from app.config import Settings
    from app.llm.factory import build_provider_from_settings

    settings = Settings(LLM_PROVIDER="auto")
    provider = build_provider_from_settings(settings)
    assert provider.active_provider().name == "echo"
