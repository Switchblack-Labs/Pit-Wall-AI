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

        race_state = None
        if request.context is not None:
            ctx = request.context.model_dump(exclude_none=True)
            if "tyre_age_laps" in ctx:
                ctx["tyre_life"] = ctx.pop("tyre_age_laps")
            if "lap" in ctx and "total_laps" in ctx:
                ctx.setdefault("laps_remaining", max(1, ctx["total_laps"] - ctx["lap"]))
            ctx.pop("lap", None)
            compound_map = {"S": "SOFT", "M": "MEDIUM", "H": "HARD",
                            "I": "INTERMEDIATE", "W": "WET"}
            if ctx.get("compound") in compound_map:
                ctx["compound"] = compound_map[ctx["compound"]]
            if "gap_s" in ctx:
                ctx.setdefault("gap_to_leader_s", ctx.pop("gap_s"))
            race_state = ctx

        result = simulate_strategy(
            request.scenario_type,
            request.laps_until_action,
            race_state=race_state,
        )

        await self.websocket_service.broadcast({
            "type": "simulation",
            "data": result.model_dump()
        })

        return result