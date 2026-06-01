from app.config import get_settings
from app.llm.factory import get_llm_provider
from app.integrations.torcs.ingest import TorcsIngestor
from app.services.race_state_service import RaceStateService
from app.services.competitor_service import CompetitorService
from app.services.websocket_service import WebSocketService
from app.services.telemetry_service import TelemetryService
from app.services.strategy_service import StrategyService
from app.services.simulation_service import SimulationService
from app.services.explanation_service import ExplanationService
from app.services.demo_service import DemoService
from app.services.torcs_service import TorcsService

race_state_service = RaceStateService()
competitor_service = CompetitorService()
websocket_service = WebSocketService()

llm_provider = get_llm_provider()

telemetry_service = TelemetryService(
    race_state_service,
    websocket_service
)

strategy_service = StrategyService(
    race_state_service,
    competitor_service,
    websocket_service
)

simulation_service = SimulationService(
    websocket_service
)

explanation_service = ExplanationService(
    race_state_service,
    websocket_service
)

demo_service = DemoService(
    telemetry_service
)

torcs_ingestor = TorcsIngestor(
    telemetry_service,
    competitor_service,
    websocket_service
)

torcs_service = TorcsService(
    torcs_ingestor
)

def get_demo_service():
    return demo_service


def get_torcs_service():
    return torcs_service


def get_explanation_service():
    return explanation_service


def get_app_settings():
    return get_settings()


def get_llm():
    """Return the process-wide LLM (Granite) provider singleton."""
    return llm_provider

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

def get_simulation_service():
    return simulation_service