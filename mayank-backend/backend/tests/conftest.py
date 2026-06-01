"""Shared pytest fixtures for the Pit Wall AI backend test suite.

Setting ``LLM_PROVIDER=echo`` at import time (before any app module is loaded)
guarantees the whole suite runs offline and deterministically — no cloud creds,
no network, no model downloads for inference.
"""

import os

# Must run before app.config / app.dependencies build the provider singleton.
os.environ.setdefault("LLM_PROVIDER", "echo")
os.environ.setdefault("LANGFLOW_URL", "")  # ensure LangFlow is treated as off

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """A FastAPI TestClient bound to the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset shared in-memory state between tests for isolation."""
    from app import dependencies

    yield
    try:
        dependencies.competitor_service.clear()
    except Exception:
        pass
    try:
        dependencies.torcs_service.stop()
    except Exception:
        pass
