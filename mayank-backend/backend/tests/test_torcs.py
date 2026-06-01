"""Tests for the TORCS integration (protocol, simulated source, ingestion)."""

import asyncio

from app.integrations.torcs.ingest import TorcsIngestor
from app.integrations.torcs.protocol import (
    encode_sensors,
    parse_sensors,
    sensors_to_telemetry_dict,
)
from app.integrations.torcs.simulator_source import SimulatedTorcsSource
from app.schemas.torcs import TorcsTelemetry
from app.services.competitor_service import CompetitorService
from app.services.race_state_service import RaceStateService
from app.services.telemetry_service import TelemetryService
from app.services.websocket_service import WebSocketService


def test_protocol_parse_and_field_map():
    s = "(speedX 23.2)(rpm 4200)(gear 3)(accel 0.8)(brake 0.0)(steer 0.05)(trackPos 0.12)(fuel 87.4)"
    parsed = parse_sensors(s)
    assert parsed["rpm"] == [4200.0]
    mapped = sensors_to_telemetry_dict(parsed)
    # speedX (m/s) -> km/h
    assert round(mapped["speed"], 1) == 83.5
    assert mapped["gear"] == 3
    assert mapped["throttle"] == 0.8


def test_protocol_encode_round_trip():
    encoded = encode_sensors({"gear": 3, "rpm": 4200})
    parsed = parse_sensors(encoded)
    assert parsed["gear"] == [3.0]
    assert parsed["rpm"] == [4200.0]


def test_simulated_source_is_seeded_and_valid():
    src = SimulatedTorcsSource(seed=7, total_laps=2, tick_seconds=0.0)

    async def collect():
        frames = []
        async for f in src.frames():
            frames.append(f)
            if len(frames) >= 5:
                src.stop()
                break
        return frames

    frames = asyncio.run(collect())
    assert len(frames) == 5
    for f in frames:
        assert isinstance(f, TorcsTelemetry)
        assert 0.0 <= f.tire_wear <= 1.0
        assert f.fuel >= 0.0
        assert f.speed >= 0.0
        # competitor tire_wear must respect [0,1] bounds (regression guard)
        for c in f.competitor_gaps:
            assert 0.0 <= c.tire_wear <= 1.0


def test_ingestor_feeds_telemetry_competitors_and_broadcasts():
    captured = []

    class FakeWS(WebSocketService):
        async def broadcast(self, payload):
            captured.append(payload)

    rss = RaceStateService()
    cs = CompetitorService()
    ws = FakeWS()
    ingestor = TorcsIngestor(TelemetryService(rss, ws), cs, ws)

    src = SimulatedTorcsSource(seed=3, total_laps=2, tick_seconds=0.0)

    async def run():
        n = 0
        async for frame in src.frames():
            await ingestor.ingest_frame(frame)
            n += 1
            if n >= 4:
                src.stop()
                break

    asyncio.run(run())

    types = {m["type"] for m in captured}
    assert "telemetry" in types
    assert "torcs" in types
    # competitors were tracked, race state updated
    assert len(cs.get_competitors()) >= 1
    assert rss.get_state().get("telemetry") is not None
    torcs_msg = next(m for m in captured if m["type"] == "torcs")
    assert {"sector_times", "race_events", "lap"} <= set(torcs_msg["data"].keys())
