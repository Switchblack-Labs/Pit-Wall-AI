from app.clients.granite_client import GraniteClient
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
        self.granite_client = GraniteClient()

    async def explain_latest_strategy(self):
        state = self.race_state_service.get_state()

        strategy = state.get("strategy")

        if not strategy:
            return {
                "error": "No strategy available"
            }

        explanation = await self.granite_client.explain_strategy(
            recommendation=strategy["recommended_action"],
            confidence=strategy["confidence"],
            risk=strategy["risk_level"],
            reasons=strategy["reason_codes"]
        )

        await self.websocket_service.broadcast({
            "type": "explanation",
            "data": explanation.model_dump()
        })

        return explanation
