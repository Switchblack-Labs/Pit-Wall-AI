import asyncio

from app.adapters.mock_adapter import MockTelemetryAdapter
from app.services.telemetry_service import TelemetryService


class DemoService:

    def __init__(
        self,
        telemetry_service: TelemetryService
    ):
        self.telemetry_service = telemetry_service
        self.adapter = MockTelemetryAdapter()
        self.running = False

    async def start(self):

        self.running = True

        while self.running:

            telemetry = self.adapter.normalize()

            await self.telemetry_service.ingest(
                telemetry
            )

            await asyncio.sleep(1)

    def stop(self):
        self.running = False