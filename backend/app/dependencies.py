from app.config import get_settings
from app.services.race_state_service import RaceStateService
from app.services.competitor_service import CompetitorService
from app.services.websocket_service import WebSocketService
from app.services.telemetry_service import TelemetryService
from app.services.strategy_service import StrategyService

race_state_service = RaceStateService()
competitor_service = CompetitorService()
websocket_service = WebSocketService()

telemetry_service = TelemetryService(
    race_state_service,
    websocket_service
)

strategy_service = StrategyService(
    race_state_service,
    competitor_service,
    websocket_service
)


def get_app_settings():
    return get_settings()

def get_strategy_service():
    return strategy_service


def get_race_state_service():
    return race_state_service


def get_competitor_service():
    return competitor_service


def get_telemetry_service():
    return telemetry_service


def get_websocket_service():
    return websocket_service