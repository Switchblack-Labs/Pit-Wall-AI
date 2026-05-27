from typing import Optional
from app.schemas.telemetry import TelemetryPayload
from app.schemas.strategy import StrategyRecommendation


class RaceState:
    def __init__(self):
        self.latest_telemetry: Optional[TelemetryPayload] = None
        self.current_strategy: Optional[StrategyRecommendation] = None
        self.active_alerts: list[str] = []

    def update_telemetry(self, telemetry: TelemetryPayload):
        self.latest_telemetry = telemetry

    def set_strategy(self, strategy: StrategyRecommendation):
        self.current_strategy = strategy

    def add_alert(self, alert: str):
        self.active_alerts.append(alert)

    def snapshot(self):
        return {
            "telemetry": self.latest_telemetry.model_dump() if self.latest_telemetry else None,
            "strategy": self.current_strategy.model_dump() if self.current_strategy else None,
            "alerts": self.active_alerts
        }