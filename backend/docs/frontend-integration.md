# Frontend Integration Guide

How a frontend connects to the Pit Wall AI backend. All shapes below are taken
directly from the live API; the authoritative, always-current schema is the
OpenAPI doc at **`/openapi.json`** (rendered at `/docs`).

## Base URL & CORS

- Local: `http://localhost:8000`
- CORS is fully open (`allow_origins=["*"]`, all methods/headers), so a browser
  app on any origin can call the API directly during the hackathon. No auth
  headers are required.

## REST endpoints

### Telemetry
`POST /api/telemetry/` — ingest one frame.
```json
{
  "speed": 210, "rpm": 9000, "gear": 6,
  "throttle": 0.9, "brake": 0.0, "steering_angle": 0.1,
  "track_position": 0.02, "lap": 12, "fuel": 42,
  "tire_wear": 0.3, "timestamp": "2026-05-28T10:00:00"
}
```
→ `{ "status": "accepted", "lap": 12 }`

`GET /api/mock/telemetry` — one synthetic frame in the same shape (handy for UI
scaffolding without a live feed).

### Competitors
`POST /api/competitors/`
```json
{ "car_id": "CAR_44", "position": 2, "gap": 1.3,
  "pit_status": false, "pace_delta": -0.2, "tire_wear": 0.4 }
```
→ `{ "status": "accepted", "car_id": "CAR_44" }`

`GET /api/competitors/` → array of the objects above.

### Strategy
`POST /api/strategy/recommend` (no body — uses current race state)
```json
{ "recommended_action": "PIT_NOW", "confidence": 0.84,
  "risk_level": "medium", "reason_codes": ["HIGH_TIRE_DEGRADATION", "LOW_TRAFFIC_WINDOW"] }
```

### Simulation
`POST /api/simulate/`
```json
{ "scenario_type": "pit_now", "laps_until_action": 0 }
```
→ `{ "projected_position": 3, "projected_gap": 2.1, "projected_risk": "low" }`

### Explanation
`POST /api/explain/` (no body — explains the latest strategy)
- `{ "explanation": "PIT_NOW recommended with 84% confidence ..." }`
- If no strategy has been generated yet: `{ "error": "No strategy available" }`
  (HTTP 200 either way — call `/api/strategy/recommend` first).

### FIA RAG
`POST /api/rag/query`
```json
{ "question": "What is the pit lane speed limit?" }
```
→
```json
{
  "question": "What is the pit lane speed limit?",
  "answer": "…",
  "citations": [ { "source": "FIA 2026 … Section B …pdf", "snippet": "…" } ],
  "grounded": true
}
```
`grounded: false` (with `citations: []`) means the answer was not found in the
regulations — render it as "not covered" rather than a confident answer.

### Demo & TORCS feeds (drive the live stream)
- `POST /api/demo/start` / `POST /api/demo/stop` — mock telemetry once/second.
- `POST /api/torcs/start` (optional body `{ "mode": "simulated", "total_laps": 58 }`)
  / `POST /api/torcs/stop` — richer TORCS-format stream.

Both push updates over the WebSocket below. `start` is idempotent.

## WebSocket — `ws://localhost:8000/ws/live`

Connect and listen. The server pushes JSON messages of the form:
```json
{ "type": "<type>", "data": { … } }
```

| `type` | `data` shape | Emitted when |
|--------|--------------|--------------|
| `telemetry` | `TelemetryPayload` (see above) | a telemetry frame is ingested (manual, demo, or TORCS) |
| `strategy` | `StrategyRecommendation` | `/api/strategy/recommend` is called |
| `simulation` | `SimulationResult` | `/api/simulate/` is called |
| `explanation` | `{ "explanation": "…" }` | `/api/explain/` is called |
| `torcs` | `{ lap, cur_lap_time, last_lap_time, sector_times, race_events, fuel, tire_wear }` | each TORCS frame (richer fields) |

Minimal client:
```js
const ws = new WebSocket("ws://localhost:8000/ws/live");
ws.onmessage = (e) => {
  const { type, data } = JSON.parse(e.data);
  switch (type) {
    case "telemetry":   updateGauges(data); break;
    case "strategy":    showRecommendation(data); break;
    case "simulation":  showProjection(data); break;
    case "explanation": showExplanation(data.explanation); break;
    case "torcs":       updateLapTiming(data); break;
  }
};
```
The connection accepts inbound text frames but ignores them; it is a one-way
broadcast for the UI. Dead connections are pruned server-side on send failure.

## Suggested demo flow for the UI

1. Open the WebSocket.
2. `POST /api/torcs/start` (or `/api/demo/start`) → telemetry + `torcs` messages
   begin streaming; render gauges and lap timing.
3. `POST /api/strategy/recommend` → `strategy` message; render the call.
4. `POST /api/explain/` → `explanation` message; render the rationale.
5. `POST /api/rag/query` for regulation lookups (answer + citations panel).
6. `POST /api/torcs/stop` when done.

## Notes

- All new response fields (`citations`, `grounded`) are additive; existing
  fields are unchanged, so older clients keep working.
- Strategy/simulation responses are currently produced by placeholder engines
  (fixed values) — see the backend README "Known limitations". The shapes are
  final and safe to build against.
