from app.engine.strategy_engine import recommend_strategy
from app.services.race_state_service import RaceStateService
from app.services.competitor_service import CompetitorService
from app.services.websocket_service import WebSocketService


class StrategyService:
    def __init__(
        self,
        race_state_service: RaceStateService,
        competitor_service: CompetitorService,
        websocket_service: WebSocketService
    ):
        self.race_state_service = race_state_service
        self.competitor_service = competitor_service
        self.websocket_service = websocket_service

    async def generate_recommendation(self):
        race_state = self.race_state_service.get_state()
        competitors = self.competitor_service.get_competitors()

        recommendation = recommend_strategy(
            race_state,
            competitors
        )

        self.race_state_service.set_strategy(recommendation)

        await self.websocket_service.broadcast({
            "type": "strategy",
            "data": recommendation.model_dump()
        })

        return recommendation