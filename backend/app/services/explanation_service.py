from app.orchestration.explainability_workflow import ExplainabilityWorkflow
from app.schemas.ai import AIExplanationResponse
from app.services.race_state_service import RaceStateService
from app.services.websocket_service import WebSocketService


class ExplanationService:
    def __init__(
        self,
        race_state_service: RaceStateService,
        websocket_service: WebSocketService
    ):
        self.race_state_service = race_state_service
        self.websocket_service = websocket_service
        # Source-of-truth orchestration pipeline (LangFlow-optional, with an
        # in-process Granite fallback). Replaces the direct GraniteClient call
        # while preserving this service's public behaviour.
        self.workflow = ExplainabilityWorkflow()

    async def explain_latest_strategy(self):
        state = self.race_state_service.get_state()

        strategy = state.get("strategy")

        if not strategy:
            return {
                "error": "No strategy available"
            }

        result = await self.workflow.run(
            recommendation=strategy["recommended_action"],
            confidence=strategy["confidence"],
            risk_level=strategy["risk_level"],
            reason_codes=strategy["reason_codes"],
        )

        explanation = AIExplanationResponse(explanation=result["explanation"])

        await self.websocket_service.broadcast({
            "type": "explanation",
            "data": explanation.model_dump()
        })

        return explanation
