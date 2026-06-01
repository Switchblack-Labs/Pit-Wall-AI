"""Explainability workflow (source of truth).

Pipeline: Recommendation -> Reasoning -> Granite -> Explanation.

The steps map 1:1 to ``langflow/flows/explainability_workflow.json``. The
in-process implementation reuses :class:`app.clients.granite_client.GraniteClient`
(which itself wraps the swappable Granite provider with a deterministic
fallback), so an explanation is always produced even offline. A configured
LangFlow server is tried first, with automatic fallback in-process.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.clients.granite_client import GraniteClient
from app.orchestration.langflow_client import LangFlowClient, get_langflow_client

FLOW_ID = "explainability_workflow"


class ExplainabilityWorkflow:
    """Turns a strategy recommendation into a natural-language explanation."""

    def __init__(
        self,
        granite_client: Optional[GraniteClient] = None,
        langflow_client: Optional[LangFlowClient] = None,
    ) -> None:
        self._granite = granite_client or GraniteClient()
        self._langflow = langflow_client or get_langflow_client()

    async def run(
        self,
        recommendation: str,
        confidence: float,
        risk_level: str,
        reason_codes: List[str],
    ) -> Dict[str, Any]:
        """Return ``{explanation, source}``."""
        if self._langflow.is_enabled():
            lf = self._langflow.run_flow(
                FLOW_ID,
                {
                    "recommendation": recommendation,
                    "confidence": confidence,
                    "risk_level": risk_level,
                    "reason_codes": reason_codes,
                },
            )
            explanation = self._parse_langflow_result(lf)
            if explanation is not None:
                return {"explanation": explanation, "source": "langflow"}

        result = await self._granite.explain_strategy(
            recommendation=recommendation,
            confidence=confidence,
            risk=risk_level,
            reasons=reason_codes,
        )
        return {"explanation": result.explanation, "source": "in_process"}

    @staticmethod
    def _parse_langflow_result(lf: Optional[Dict[str, Any]]) -> Optional[str]:
        if not lf:
            return None
        return lf.get("explanation") or lf.get("result") or lf.get("text")
