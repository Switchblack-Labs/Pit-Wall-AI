# Pit Wall AI — Frontend Integration Contract

This is the **stable contract**. Build the page against this now.
The ML models are still retraining in the background, but the request/response
**shapes never change** — only the numbers inside the response do.

## TL;DR for the teammate

- **Use the API, not a Python import.** Cleaner boundary, you don't need our ML deps,
  and we can keep retraining without breaking your build.
- **Yes, sample-data-then-predict is exactly the right UX.** There's an endpoint that
  hands you an editable example state; the user tweaks it, you POST it back, you get a call.
- **Yes, the output is piped through Granite.** The response includes both the structured
  call (for badges/colors) and a Granite natural-language `explanation` (for the pit-wall text box).

## Base URL
`http://localhost:8000` (FastAPI). Interactive docs at `/docs`.

---

## 1. Seed the form — `GET /api/v1/sample-state`

Returns an editable example race state. Render these as form fields.

```json
{
  "circuit": "bahrain",
  "compound": "MEDIUM",
  "tyre_life": 28,
  "laps_remaining": 22,
  "total_laps": 57,
  "position": 4,
  "gap_ahead_s": 1.8,
  "gap_behind_s": 4.5,
  "pit_loss_s": 22.3,
  "track_temp": 38.0,
  "track_status": "1",
  "compounds_used": "SOFT",
  "stops_made": 1,
  "competitors": null
}
```

## 2. Get a pit call — `POST /api/v1/recommend`

**Body:** same shape as above (send the user's edited values). All fields optional;
omitted ones use sane defaults.

**Field reference (inputs):**

| field | type | meaning |
|---|---|---|
| `circuit` | string | canonical name: `bahrain`, `monaco`, `monza`, `silverstone`, … |
| `compound` | string | `SOFT` \| `MEDIUM` \| `HARD` \| `INTERMEDIATE` \| `WET` |
| `tyre_life` | int | laps on current tyre |
| `laps_remaining` | int | laps left |
| `total_laps` | int | race length |
| `position` | int | current track position |
| `gap_ahead_s` | float | seconds to car ahead |
| `gap_behind_s` | float | seconds to car behind |
| `pit_loss_s` | float | pit time loss at this circuit |
| `track_temp` | float | °C |
| `track_status` | string | `1`=green `2`=yellow `4`=SafetyCar `5`=red `6`=VSC |
| `compounds_used` | string | comma list already used, e.g. `"SOFT,MEDIUM"` |
| `stops_made` | int | stops so far |
| `deg_rate` | float? | optional measured deg; engine predicts if omitted |
| `competitors` | array? | `[{position, compound, tyre_life}]` rivals near you |

**Response (`FullRecommendation`):**

```json
{
  "recommended_action": "PIT_HARD",
  "confidence": 0.85,
  "risk_level": "medium",
  "reason_codes": ["HIGH_DEGRADATION", "UNDERCUT_VIABLE"],
  "explanation": "Box this lap. The mediums are past their cliff and Sainz behind is in undercut range — covering now protects P4."
}
```

**Output reference:**

| field | values | use in UI |
|---|---|---|
| `recommended_action` | `PIT_SOFT` \| `PIT_MEDIUM` \| `PIT_HARD` \| `STAY_OUT` | big call badge |
| `confidence` | `0.0`–`1.0` | confidence meter |
| `risk_level` | `low` \| `medium` \| `high` | color (green/amber/red) |
| `reason_codes` | see below | factor chips |
| `explanation` | Granite text | pit-wall message box |

**Possible `reason_codes`:** `CRITICAL_TYRE_WEAR`, `EXTREME_DEGRADATION`,
`HIGH_DEGRADATION`, `MODERATE_DEGRADATION`, `UNDERCUT_VIABLE`,
`SAFETY_CAR_PIT_WINDOW`, `SAFETY_CAR_STAY_OUT`. (`ENGINE_FALLBACK` appears only
if you hit the API before models finish loading — safe to ignore/treat as degraded.)

---

## 3. (Optional) What-if sim — `POST /api/strategy/simulate`-style

Engine also supports projecting a scenario. Input `{scenario_type, laps_until_action}`
→ `{projected_position, projected_gap, projected_risk}`. Ask if you want this wired to
the same v1 surface.

---

## Notes
- Granite: if `GRANITE_API_KEY` / `GRANITE_URL` env vars aren't set, `explanation`
  falls back to a clean templated sentence — still a valid string, page won't break.
- CORS is open (`*`), so you can hit it from the dev frontend directly.
- Endpoint is **non-blocking on the retrain** — it returns real calls now, better calls later.
