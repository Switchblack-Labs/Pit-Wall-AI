"""
Strategy engine powered by ml_engine.
Drop-in replacement: returns StrategyRecommendation Pydantic model.
"""
import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from app.schemas.strategy import StrategyRecommendation
from ml_engine.integration import get_engine


def recommend_strategy(race_state, competitors):
    """
    Takes race_state (dict or object with .snapshot()) and competitors list.
    Returns StrategyRecommendation (Pydantic).
    """
    engine = get_engine()

    if hasattr(race_state, "snapshot"):
        state_dict = race_state.snapshot()
        tel = (state_dict.get("telemetry") or {})
        state_dict.update({
            "tyre_life": int(tel.get("tire_wear", 0.5) * 40),
            "compound": tel.get("compound", "MEDIUM"),
            "laps_remaining": max(1, state_dict.get("total_laps", 57) - tel.get("lap", 30)),
            "position": tel.get("position", 10),
            "track_status": tel.get("track_status", "1"),
        })
    elif isinstance(race_state, dict):
        state_dict = race_state
    else:
        state_dict = {}

    comp_list = None
    if competitors:
        comp_list = []
        for c in competitors:
            if isinstance(c, dict):
                comp_list.append(c)
            elif hasattr(c, "model_dump"):
                comp_list.append(c.model_dump())
            elif hasattr(c, "__dict__"):
                comp_list.append(vars(c))

    result = engine.recommend(state_dict, comp_list)

    return StrategyRecommendation(
        recommended_action=result["recommended_action"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        reason_codes=result["reason_codes"],
    )
