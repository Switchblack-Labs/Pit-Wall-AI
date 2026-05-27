from app.schemas.telemetry import TelemetryPayload
from app.services.race_state_service import RaceStateService
from app.services.websocket_service import WebSocketService
from app.utils.logger import logger


class TelemetryService:
    def __init__(
        self,
        race_state_service: RaceStateService,
        websocket_service: WebSocketService
    ):
        self.race_state_service = race_state_service
        self.websocket_service = websocket_service

    async def ingest(self, telemetry: TelemetryPayload):
        self.race_state_service.update_telemetry(telemetry)

        logger.info(
            "Telemetry received",
            extra={
                "speed": telemetry.speed,
                "lap": telemetry.lap
            }
        )

        await self.websocket_service.broadcast({
            "type": "telemetry",
            "data": telemetry.model_dump(mode="json")
        })

        return {
            "status": "accepted",
            "lap": telemetry.lap
        }