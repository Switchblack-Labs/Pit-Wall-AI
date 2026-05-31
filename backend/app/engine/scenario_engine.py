"""
Scenario/simulation engine powered by ml_engine.
Drop-in replacement: returns SimulationResult Pydantic model.
"""
import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from app.schemas.simulation import SimulationResult
from ml_engine.integration import get_engine


def simulate_strategy(scenario_type: str, laps_until_action: int, race_state: dict = None):
    """
    Simulate a strategy scenario using the race projector.

    If `race_state` is provided (a dict of actual race conditions), the
    projection runs from that state. Any missing fields fall back to sensible
    defaults, so partial state still works. Returns SimulationResult (Pydantic).
    """
    engine = get_engine()

    # Default representative state; overlaid with any real values supplied.
    state = {
        "circuit": "bahrain",
        "compound": "MEDIUM",
        "tyre_life": 15,
        "laps_remaining": laps_until_action + 10,
        "total_laps": 57,
        "position": 5,
        "gap_ahead_s": 2.0,
        "gap_behind_s": 3.0,
        "gap_to_leader_s": 10.0,
        "pit_loss_s": 22.0,
        "track_temp": 35,
        "compounds_used": "SOFT",
        "stops_made": 1,
        "track_status": "1",
    }
    if race_state:
        # Only override with non-None values from the caller.
        state.update({k: v for k, v in race_state.items() if v is not None})

    decision_map = {
        "pit_now": "PIT_MEDIUM",
        "pit_soft": "PIT_SOFT",
        "pit_medium": "PIT_MEDIUM",
        "pit_hard": "PIT_HARD",
        "stay_out": "STAY_OUT",
    }
    decision = decision_map.get(scenario_type, "STAY_OUT")

    proj = engine.projector.project(state, decision)

    pos = proj["projected_position"]
    if pos <= 3:
        risk = "low"
    elif pos <= 6:
        risk = "medium"
    else:
        risk = "high"

    return SimulationResult(
        projected_position=pos,
        projected_gap=round(proj["projected_total_time"], 1),
        projected_risk=risk,
    )
