"""
Smoke test: verify backend engine drop-in files work correctly.
Run from project root: python ml_engine/tests/test_integration.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Simulate what the backend does
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend"))

from app.engine.strategy_engine import recommend_strategy
from app.engine.scenario_engine import simulate_strategy
from app.schemas.strategy import StrategyRecommendation
from app.schemas.simulation import SimulationResult


def test_strategy_engine():
    """Test recommend_strategy returns proper Pydantic model."""
    race_state = {
        "circuit": "bahrain",
        "compound": "MEDIUM",
        "tyre_life": 20,
        "laps_remaining": 25,
        "total_laps": 57,
        "position": 4,
        "gap_ahead_s": 1.5,
        "gap_behind_s": 2.0,
        "gap_to_leader_s": 8.0,
        "pit_loss_s": 22.0,
        "track_temp": 38,
        "compounds_used": "SOFT",
        "stops_made": 1,
        "track_status": "1",
        "deg_rate": 0.12,
    }
    competitors = [
        {"position": 3, "compound": "HARD", "tyre_life": 10},
        {"position": 5, "compound": "MEDIUM", "tyre_life": 18},
    ]

    result = recommend_strategy(race_state, competitors)

    assert isinstance(result, StrategyRecommendation), f"Expected StrategyRecommendation, got {type(result)}"
    assert result.recommended_action in ("STAY_OUT", "PIT_SOFT", "PIT_MEDIUM", "PIT_HARD"), f"Unexpected action: {result.recommended_action}"
    assert 0 <= result.confidence <= 1, f"Confidence out of range: {result.confidence}"
    assert result.risk_level in ("low", "medium", "high"), f"Unexpected risk: {result.risk_level}"
    assert isinstance(result.reason_codes, list), f"reason_codes not a list"

    print(f"  Action: {result.recommended_action}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Risk: {result.risk_level}")
    print(f"  Codes: {result.reason_codes}")
    print("  PASS")


def test_scenario_engine():
    """Test simulate_strategy returns proper Pydantic model."""
    for scenario in ["pit_now", "stay_out", "pit_hard", "unknown_scenario"]:
        result = simulate_strategy(scenario, laps_until_action=10)
        assert isinstance(result, SimulationResult), f"Expected SimulationResult, got {type(result)}"
        assert isinstance(result.projected_position, int)
        assert isinstance(result.projected_gap, float)
        assert result.projected_risk in ("low", "medium", "high")
        print(f"  {scenario}: P{result.projected_position}, gap={result.projected_gap}s, risk={result.projected_risk}")

    print("  PASS")


def test_model_dump():
    """Test .model_dump() works (used by websocket broadcast)."""
    state = {"circuit": "bahrain", "compound": "MEDIUM", "tyre_life": 15}
    result = recommend_strategy(state, None)
    dumped = result.model_dump()
    assert "recommended_action" in dumped
    assert "confidence" in dumped
    assert "risk_level" in dumped
    assert "reason_codes" in dumped
    print(f"  model_dump keys: {list(dumped.keys())}")
    print("  PASS")


if __name__ == "__main__":
    print("=" * 50)
    print("BACKEND INTEGRATION SMOKE TEST")
    print("=" * 50)

    print("\n1. Strategy Engine:")
    test_strategy_engine()

    print("\n2. Scenario Engine:")
    test_scenario_engine()

    print("\n3. Pydantic model_dump():")
    test_model_dump()

    print("\n" + "=" * 50)
    print("ALL INTEGRATION TESTS PASSED")
    print("=" * 50)
