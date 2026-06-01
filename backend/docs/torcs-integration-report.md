# TORCS Integration Report

> Usage + live-connection guide: [`torcs-integration.md`](./torcs-integration.md).
> This report summarizes what was built, the design, and verification.

## Decision

TORCS is added as a **race telemetry source**, fully **additive**: it reuses the
existing telemetry/competitor/WebSocket services and shared race state, so the
manual `/api/telemetry` flow is unaffected. The default source is a built-in
generator, so the feature runs end-to-end with **no TORCS install**.

## Delivered

| Artifact | Role |
|----------|------|
| `app/schemas/torcs.py` | `TorcsTelemetry` (+ `TorcsCompetitorGap`): speed, rpm, gear, fuel, tire_wear, track_position, lap, **sector_times, race_events, competitor_gaps** |
| `app/integrations/torcs/protocol.py` | Pure-function SCR sensor-string parse/encode + `SCR_FIELD_MAP` |
| `app/integrations/torcs/source.py` | `TorcsSource` ABC (`frames()` async iterator, `stop()`) |
| `app/integrations/torcs/simulator_source.py` | **Default** built-in generator (tire deg, fuel burn, lap/sector progression, race events, competitor gaps); seedable |
| `app/integrations/torcs/live_source.py` | Real SCR/UDP source — plug-and-play swap |
| `app/integrations/torcs/ingest.py` | Maps frames → existing `TORCSTelemetryAdapter` → telemetry/competitor services + WebSocket |
| `app/services/torcs_service.py` | Start/stop streaming (mirrors `DemoService` pattern) |
| `app/api/torcs.py` | `POST /api/torcs/start` (sim default), `POST /api/torcs/stop` |

## Data flow

Each simulated frame produces two WebSocket messages: `telemetry` (canonical
`TelemetryPayload`, unchanged contract) and `torcs` (richer fields: sector
times, race events, lap timing, fuel, tire wear). Because data lands in the
shared `RaceStateService`, the strategy/simulation/explanation endpoints consume
it automatically.

## Reuse (no duplication)

The legacy `app/adapters/torcs_adapter.py` (`TORCSTelemetryAdapter.normalize`)
is reused as-is via `TorcsTelemetry.to_adapter_dict()` rather than writing a new
mapping. Start/stop mirrors the existing demo async-task pattern.

## Live TORCS path

`LiveTorcsSource` binds a UDP socket, parses SCR datagrams with the protocol
helpers, and maps them via `SCR_FIELD_MAP`. Switching from simulated to live is
only the `mode` parameter — same interface, same ingestor. SCR-absent fields
(lap/tire/fuel) currently default safely; extend `_frame_from_payload` with a
track model to populate them. Full instructions in `torcs-integration.md`.

## Bug found & fixed during verification

Competitor `tire_wear` could go negative (`min(1.0, wear + uniform(-0.1,0.2))`
clamped only the top), failing `TorcsCompetitorGap` validation. Fixed with a
two-sided clamp. Covered by a regression assertion in `tests/test_torcs.py`.

## Verification (`tests/test_torcs.py`, offline)

Protocol parse + field map (speedX m/s → km/h) and encode round-trip; seeded
simulator produces bounds-valid frames; ingestor feeds telemetry + competitors +
both broadcast channels and updates race state. Start/stop endpoints covered in
`tests/test_api_endpoints.py`.

## Limitation

The streaming loop uses `asyncio.create_task`; a full streaming round-trip
through `TestClient`'s WebSocket portal deadlocks (a test-harness artifact, not a
runtime bug), so streaming is verified by driving the ingestor directly. The
endpoints' start/stop and the component pipeline are both tested.
