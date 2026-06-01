from app.state.race_state import RaceState
from app.schemas.telemetry import TelemetryPayload
from app.schemas.strategy import StrategyRecommendation


class RaceStateService:
    def __init__(self):
        self.state = RaceState()

    def update_telemetry(self, telemetry: TelemetryPayload):
        self.state.update_telemetry(telemetry)

    def set_strategy(self, strategy: StrategyRecommendation):
        self.state.set_strategy(strategy)

    def add_alert(self, alert: str):
        self.state.add_alert(alert)

    def get_state(self):
        return self.state.snapshot()