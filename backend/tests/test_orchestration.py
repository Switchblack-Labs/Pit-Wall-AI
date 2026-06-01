"""Tests for the orchestration layer (workflows + optional LangFlow client)."""

import asyncio

from app.orchestration.explainability_workflow import ExplainabilityWorkflow
from app.orchestration.fia_workflow import FiaWorkflow
from app.orchestration.langflow_client import LangFlowClient


def test_langflow_client_disabled_when_no_url():
    client = LangFlowClient(base_url="")
    assert client.is_enabled() is False
    assert client.run_flow("any", {"q": 1}) is None


def test_fia_workflow_runs_in_process_when_langflow_off():
    wf = FiaWorkflow(langflow_client=LangFlowClient(base_url=""))
    result = wf.run("What is the pit lane speed limit?")
    assert result["source"] == "in_process"
    assert result["answer"]
    assert "citations" in result and "grounded" in result


def test_fia_workflow_uses_langflow_when_available():
    class FakeLF(LangFlowClient):
        def __init__(self):
            super().__init__(base_url="http://fake")

        def run_flow(self, flow_id, payload):
            return {"answer": "from langflow", "citations": [], "grounded": True}

    wf = FiaWorkflow(langflow_client=FakeLF())
    result = wf.run("anything")
    assert result["source"] == "langflow"
    assert result["answer"] == "from langflow"


def test_fia_workflow_falls_back_when_langflow_returns_nothing():
    class EmptyLF(LangFlowClient):
        def __init__(self):
            super().__init__(base_url="http://fake")

        def run_flow(self, flow_id, payload):
            return None

    wf = FiaWorkflow(langflow_client=EmptyLF())
    result = wf.run("What is the pit lane speed limit?")
    assert result["source"] == "in_process"


def test_explainability_workflow_in_process():
    wf = ExplainabilityWorkflow(langflow_client=LangFlowClient(base_url=""))
    result = asyncio.run(
        wf.run("PIT_NOW", 0.84, "medium", ["HIGH_TIRE_DEGRADATION"])
    )
    assert result["source"] == "in_process"
    assert "PIT_NOW" in result["explanation"]
