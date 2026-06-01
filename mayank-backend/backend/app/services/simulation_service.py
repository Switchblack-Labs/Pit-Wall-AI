from app.engine.scenario_engine import simulate_strategy
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResult
)
from app.services.websocket_service import WebSocketService


class SimulationService:
    def __init__(
        self,
        websocket_service: WebSocketService
    ):
        self.websocket_service = websocket_service

    async def run_simulation(
        self,
        request: SimulationRequest
    ) -> SimulationResult:

        result = simulate_strategy(
            request.scenario_type,
            request.laps_until_action
        )

        await self.websocket_service.broadcast({
            "type": "simulation",
            "data": result.model_dump()
        })

        return result