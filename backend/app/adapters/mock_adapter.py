from datetime import datetime
from random import uniform, randint

from app.adapters.base_adapter import BaseTelemetryAdapter
from app.schemas.telemetry import TelemetryPayload


class MockTelemetryAdapter(BaseTelemetryAdapter):

    def normalize(self, raw_data=None) -> TelemetryPayload:

        return TelemetryPayload(
            speed=uniform(180, 330),
            rpm=randint(8000, 12000),
            gear=randint(4, 8),
            throttle=uniform(0.5, 1.0),
            brake=uniform(0.0, 0.2),
            steering_angle=uniform(-0.2, 0.2),
            track_position=uniform(-1.0, 1.0),
            lap=randint(1, 70),
            fuel=uniform(5, 100),
            tire_wear=uniform(0.1, 0.9),
            timestamp=datetime.utcnow()
        )