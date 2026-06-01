# TORCS Integration

TORCS (The Open Racing Car Simulator) is wired in as a **race telemetry
source**. The integration is **additive**: it reuses the existing telemetry,
competitor and WebSocket services, so the manual `/api/telemetry` flow is
unchanged.

```
 ┌──────────────┐   frames   ┌──────────────┐   TelemetryPayload   ┌──────────────────┐
 │ TorcsSource  │ ─────────▶ │ TorcsIngestor│ ───────────────────▶ │ TelemetryService │─┐
 │ (sim | live) │            │  (mapping)   │                      └──────────────────┘ │
 └──────────────┘            │              │   CompetitorPayload  ┌──────────────────┐ │ broadcast
                             │              │ ───────────────────▶ │ CompetitorService│ │ /ws/live
                             │              │   torcs extras       └──────────────────┘ │
                             └──────────────┘ ─────────────────────────────────────────┘
```

Everything downstream (strategy, simulation, explanation endpoints) reads the
same `RaceStateService`, so TORCS data flows to them automatically.

## Components (`app/integrations/torcs/`)

| File | Role |
|------|------|
| `protocol.py` | Pure-function SCR sensor-string `parse`/`encode` + `SCR_FIELD_MAP`. |
| `source.py` | `TorcsSource` ABC: async `frames()` iterator + `stop()`. |
| `simulator_source.py` | **Default.** `SimulatedTorcsSource` — built-in generator (tire deg, fuel burn, laps/sectors, race events, competitor gaps). No TORCS install needed. |
| `live_source.py` | `LiveTorcsSource` — reads SCR sensor datagrams over UDP from a real TORCS server. Plug-and-play swap. |
| `ingest.py` | `TorcsIngestor` — maps frames onto existing services via the existing `TORCSTelemetryAdapter`. |

Schema: `app/schemas/torcs.py` (`TorcsTelemetry`, `TorcsCompetitorGap`).
Service: `app/services/torcs_service.py`. API: `app/api/torcs.py`.

## Usage (simulated — default)

```bash
# start streaming simulated TORCS telemetry
curl -X POST localhost:8000/api/torcs/start \
     -H 'Content-Type: application/json' \
     -d '{"mode":"simulated","total_laps":58}'

# observe the stream
#   ws://localhost:8000/ws/live   → messages of type "telemetry" and "torcs"

# stop
curl -X POST localhost:8000/api/torcs/stop
```

`start` is idempotent (a second call while running is a no-op). The stream emits
two WebSocket message types per frame:
* `telemetry` — the canonical `TelemetryPayload` (unchanged contract).
* `torcs` — the richer TORCS-only fields: `lap`, `cur_lap_time`,
  `last_lap_time`, `sector_times`, `race_events`, `fuel`, `tire_wear`.

## Connecting a real TORCS (live mode)

Live mode targets TORCS running the **SCR (Simulated Car Racing) patch**, which
streams sensor strings over UDP.

1. Install TORCS + the SCR `scr-server` patch.
2. Launch a race configured with the SCR server bot; note its UDP port
   (default `3001`).
3. Start the backend source in live mode:

   ```bash
   curl -X POST localhost:8000/api/torcs/start \
        -d '{"mode":"live","host":"127.0.0.1","port":3001}'
   ```

`LiveTorcsSource` binds the UDP socket, parses each datagram with
`protocol.parse_sensors`, and maps it via `SCR_FIELD_MAP`. Fields SCR does not
expose directly (lap count, tire wear, fuel) currently default to safe values;
extend `live_source._frame_from_payload` with your track model to populate them.

Because both sources implement the same `TorcsSource` interface and feed the
same `TorcsIngestor`, switching from simulated to live changes only the `mode`
parameter — no downstream code changes.

## Notes

* `speedX` (m/s) is converted to km/h to match `TelemetryPayload`.
* The simulated source is seedable (`seed=`) for deterministic tests.
* The streaming loop is cancelled cleanly on `/api/torcs/stop` and on app
  shutdown (see the `lifespan` handler in `app/main.py`).
