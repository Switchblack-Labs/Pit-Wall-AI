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

        # Pass through any real race-state fields the caller supplied; the
        # engine overlays them on its defaults (scenario_type/laps_until_action
        # are handled separately, so exclude them from the state dict).
        race_state = request.model_dump(
            exclude={"scenario_type", "laps_until_action"},
            exclude_none=True,
        )

        result = simulate_strategy(
            request.scenario_type,
            request.laps_until_action,
            race_state or None,
        )

        await self.websocket_service.broadcast({
            "type": "simulation",
            "data": result.model_dump()
        })

        return result