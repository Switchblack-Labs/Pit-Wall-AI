from abc import ABC, abstractmethod
from app.schemas.telemetry import TelemetryPayload


class BaseTelemetryAdapter(ABC):

    @abstractmethod
    def normalize(self, raw_data) -> TelemetryPayload:
        pass