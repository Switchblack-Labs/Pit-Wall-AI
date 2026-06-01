"""FIA regulations workflow (source of truth).

Pipeline: Question -> Retriever -> Context Builder -> Granite -> Answer.

The steps map 1:1 to the nodes in ``langflow/flows/fia_workflow.json``. The
in-process implementation reuses the existing, working RAG chain
(:func:`app.rag.rag_chain.answer_question`) so retrieval/embeddings/ChromaDB are
untouched. If a LangFlow server is configured it is tried first, with automatic
fallback to the in-process pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.orchestration.langflow_client import LangFlowClient, get_langflow_client
from app.rag.rag_chain import answer_question

FLOW_ID = "fia_workflow"


class FiaWorkflow:
    """Orchestrates an FIA regulations question into a grounded answer."""

    def __init__(self, langflow_client: Optional[LangFlowClient] = None) -> None:
        self._langflow = langflow_client or get_langflow_client()

    def run(self, question: str) -> Dict[str, Any]:
        """Return ``{answer, citations, grounded, source}``.

        ``source`` is ``"langflow"`` or ``"in_process"`` so callers/tests can
        see which path served the request.
        """
        if self._langflow.is_enabled():
            lf = self._langflow.run_flow(FLOW_ID, {"question": question})
            parsed = self._parse_langflow_result(lf)
            if parsed is not None:
                parsed["source"] = "langflow"
                return parsed

        result = answer_question(question)
        return {
            "answer": result["answer"],
            "citations": result["citations"],
            "grounded": result["grounded"],
            "source": "in_process",
        }

    @staticmethod
    def _parse_langflow_result(lf: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Best-effort extraction of an answer from a LangFlow response."""
        if not lf:
            return None
        answer = (
            lf.get("answer")
            or lf.get("result")
            or lf.get("text")
        )
        if not answer:
            return None
        return {
            "answer": answer,
            "citations": lf.get("citations", []),
            "grounded": lf.get("grounded", True),
        }
