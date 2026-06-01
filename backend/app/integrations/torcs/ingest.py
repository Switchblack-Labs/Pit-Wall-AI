"""TORCS -> backend ingestion.

Maps each :class:`TorcsTelemetry` frame onto the existing backend flow, reusing
components rather than duplicating them:

* core sensors -> ``TORCSTelemetryAdapter.normalize()`` -> ``TelemetryPayload``
  -> ``TelemetryService.ingest()`` (updates race state + broadcasts "telemetry")
* ``competitor_gaps`` -> ``CompetitorPayload`` -> ``CompetitorService.update_competitor()``
* ``race_events`` / ``sector_times`` -> a ``torcs`` WebSocket broadcast for the
  richer fields the canonical telemetry schema does not carry.

This keeps the TORCS feature additive: it touches the same services as the
manual ``/api/telemetry`` endpoint and introduces no parallel state.
"""

from __future__ import annotations

from app.adapters.torcs_adapter import TORCSTelemetryAdapter
from app.schemas.competitors import CompetitorPayload
from app.schemas.torcs import TorcsTelemetry
from app.services.competitor_service import CompetitorService
from app.services.telemetry_service import TelemetryService
from app.services.websocket_service import WebSocketService


class TorcsIngestor:
    """Routes TORCS frames into telemetry, competitor and WebSocket layers."""

    def __init__(
        self,
        telemetry_service: TelemetryService,
        competitor_service: CompetitorService,
        websocket_service: WebSocketService,
    ) -> None:
        self.telemetry_service = telemetry_service
        self.competitor_service = competitor_service
        self.websocket_service = websocket_service
        self.adapter = TORCSTelemetryAdapter()

    async def ingest_frame(self, frame: TorcsTelemetry) -> None:
        telemetry = self.adapter.normalize(frame.to_adapter_dict())
        await self.telemetry_service.ingest(telemetry)

        for comp in frame.competitor_gaps:
            self.competitor_service.update_competitor(
                CompetitorPayload(
                    car_id=comp.car_id,
                    position=comp.position,
                    gap=comp.gap,
                    pit_status=comp.pit_status,
                    pace_delta=comp.pace_delta,
                    tire_wear=comp.tire_wear,
                )
            )

        await self.websocket_service.broadcast(
            {
                "type": "torcs",
                "data": {
                    "lap": frame.lap,
                    "cur_lap_time": frame.cur_lap_time,
                    "last_lap_time": frame.last_lap_time,
                    "sector_times": frame.sector_times,
                    "race_events": frame.race_events,
                    "fuel": frame.fuel,
                    "tire_wear": frame.tire_wear,
                },
            }
        )
