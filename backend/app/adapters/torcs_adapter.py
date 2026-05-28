from app.adapters.base_adapter import BaseTelemetryAdapter
from app.schemas.telemetry import TelemetryPayload


class TORCSTelemetryAdapter(BaseTelemetryAdapter):

    def normalize(self, raw_data) -> TelemetryPayload:

        return TelemetryPayload(
            speed=raw_data["speed"],
            rpm=raw_data["rpm"],
            gear=raw_data["gear"],
            throttle=raw_data["throttle"],
            brake=raw_data["brake"],
            steering_angle=raw_data["steering"],
            track_position=raw_data["track_position"],
            lap=raw_data["lap"],
            fuel=raw_data["fuel"],
            tire_wear=raw_data["tire_wear"],
            timestamp=raw_data["timestamp"]
        )