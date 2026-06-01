"""First-class orchestration layer for Pit Wall AI.

These Python workflows are the **source of truth** for multi-step AI flows.
They compose existing services (FIA RAG retrieval + Granite generation, strategy
explanation) into named, inspectable pipelines whose steps map 1:1 to the
exported LangFlow graphs in ``langflow/flows/``.

LangFlow is **optional**: when ``LANGFLOW_URL`` is configured, a workflow may
delegate to a running LangFlow server; otherwise (and on any error) it runs the
in-process pipeline. The backend therefore runs fully without LangFlow
installed or reachable.
"""

from app.orchestration.explainability_workflow import ExplainabilityWorkflow
from app.orchestration.fia_workflow import FiaWorkflow
from app.orchestration.langflow_client import LangFlowClient, get_langflow_client

__all__ = [
    "FiaWorkflow",
    "ExplainabilityWorkflow",
    "LangFlowClient",
    "get_langflow_client",
]
