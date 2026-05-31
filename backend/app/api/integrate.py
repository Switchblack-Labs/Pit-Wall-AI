"""
Integration API — the single surface your teammate builds the frontend against.

Two endpoints:
  GET  /api/v1/sample-state   -> an editable example RaceState (seed the form)
  POST /api/v1/recommend      -> RaceState in, recommendation + Granite text out

Self-contained and defensive: if the ML engine or Granite isn't ready yet
(models still training in the background), it degrades gracefully instead of 500ing,
so the frontend can be built end-to-end today.
"""
from fastapi import APIRouter

from app.schemas.integrate import RaceStateInput, FullRecommendation
from app.clients.granite_client import GraniteClient

router = APIRouter(prefix="/api/v1", tags=["integration"])

_granite = GraniteClient()

_GRANITE_SYSTEM = (
    "You are an F1 race strategist on the pit wall. Given a structured pit "
    "recommendation and the current race state, write ONE concise, confident "
    "sentence (max ~30 words) telling the driver what to do and why. No preamble."
)


def _template_explanation(rec: dict, state: dict) -> str:
    """Deterministic fallback so `explanation` is always a valid string,
    even if Granite is unconfigured or unreachable."""
    action = rec["recommended_action"].replace("_", " ").title()
    reasons = ", ".join(r.replace("_", " ").lower() for r in rec["reason_codes"]) or "current pace"
    return (
        f"{action}: P{state.get('position', '?')} with {state.get('tyre_life', '?')} laps on "
        f"{state.get('compound', 'tyres')}, {state.get('laps_remaining', '?')} to go — driven by {reasons}."
    )


async def _explain(rec: dict, state: dict) -> str:
    """Pipe the structured call through Granite; fall back to a template on any error."""
    prompt = (
        f"Recommendation: {rec['recommended_action']} "
        f"(confidence {rec['confidence']:.0%}, risk {rec['risk_level']}). "
        f"Reason codes: {', '.join(rec['reason_codes'])}. "
        f"Race state: {state}."
    )
    try:
        text = await _granite.generate(prompt, system=_GRANITE_SYSTEM)
        return (text or "").strip() or _template_explanation(rec, state)
    except Exception:
        return _template_explanation(rec, state)


def _get_recommendation(state: dict, competitors):
    """Call the ml_engine strategy engine. Falls back to a deterministic
    heuristic if the engine/models aren't importable yet (background retrain)."""
    try:
        from ml_engine.integration import get_engine
        engine = get_engine()
        return engine.recommend(state, competitors)
    except Exception:
        # Engine not ready (models retraining). Minimal heuristic so the UI still works.
        tyre_life = state.get("tyre_life", 15)
        laps_remaining = state.get("laps_remaining", 25)
        if str(state.get("track_status")) in ("4", "6"):
            return {
                "recommended_action": "PIT_MEDIUM",
                "confidence": 0.8,
                "risk_level": "low",
                "reason_codes": ["SAFETY_CAR_PIT_WINDOW", "ENGINE_FALLBACK"],
            }
        if tyre_life > 30 and laps_remaining > 5:
            return {
                "recommended_action": "PIT_HARD",
                "confidence": 0.7,
                "risk_level": "medium",
                "reason_codes": ["HIGH_DEGRADATION", "ENGINE_FALLBACK"],
            }
        return {
            "recommended_action": "STAY_OUT",
            "confidence": 0.6,
            "risk_level": "low",
            "reason_codes": ["ENGINE_FALLBACK"],
        }


@router.get("/sample-state", response_model=RaceStateInput)
async def sample_state() -> RaceStateInput:
    """Editable example state to seed the UI form. The user tweaks these
    values, POSTs them to /recommend, and gets a pit call back."""
    return RaceStateInput(
        circuit="bahrain",
        compound="MEDIUM",
        tyre_life=28,
        laps_remaining=22,
        total_laps=57,
        position=4,
        gap_ahead_s=1.8,
        gap_behind_s=4.5,
        pit_loss_s=22.3,
        track_temp=38.0,
        track_status="1",
        compounds_used="SOFT",
        stops_made=1,
        competitors=None,
    )


@router.post("/recommend", response_model=FullRecommendation)
async def recommend(state: RaceStateInput) -> FullRecommendation:
    """Take a race state, return the structured pit call PLUS a Granite-written
    natural-language explanation for the pit-wall display."""
    payload = state.model_dump()
    competitors = payload.pop("competitors", None)

    rec = _get_recommendation(payload, competitors)
    explanation = await _explain(rec, payload)

    return FullRecommendation(
        recommended_action=rec["recommended_action"],
        confidence=rec["confidence"],
        risk_level=rec["risk_level"],
        reason_codes=rec["reason_codes"],
        explanation=explanation,
    )
