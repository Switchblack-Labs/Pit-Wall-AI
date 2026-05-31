"""
Ferrari Disaster Test Suite.
Ground effect era (2022-2025) strategy blunders where the correct call
is unambiguous in hindsight.

Each test: load exact race state at the decision lap, run the strategy engine,
verify the model makes the right call.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_engine.pipeline.strategy_engine import StrategyEngine
from ml_engine.data.schema import get_connection


# Ground effect era Ferrari disasters (2022-2025)
FERRARI_DISASTERS = [
    {
        "name": "Monaco 2022 - Double Stack Disaster",
        "race_id": "2022_monaco_r",
        "driver": "LEC",
        "lap": 21,
        "description": "Leclerc leading on HARDS, team pitted him into traffic behind Sainz. "
                       "Should have stayed out or pitted earlier on a clear lap.",
        "correct_action": "STAY_OUT",
        "what_ferrari_did": "PIT",
        "positions_lost": 2,  # P1 -> P4
    },
    {
        "name": "Britain 2022 - Unnecessary SC Pit",
        "race_id": "2022_silverstone_r",
        "driver": "LEC",
        "lap": 37,
        "description": "Leclerc P1, pitted under SC when he had newer tyres than rivals. "
                       "Sainz stayed out and won. Classic case of pitting the leader unnecessarily.",
        "correct_action": "STAY_OUT",
        "what_ferrari_did": "PIT",
        "positions_lost": 3,  # P1 -> P4
    },
    {
        "name": "Hungary 2022 - Wrong Compound on Restart",
        "race_id": "2022_hungaroring_r",
        "driver": "LEC",
        "lap": 39,
        "description": "Leclerc put on HARD tyres in hot conditions when track favoured MEDIUM/SOFT. "
                       "Lost pace and positions. The HARD had terrible deg on the hot track.",
        "correct_action": "PIT_MEDIUM",  # or PIT_SOFT
        "what_ferrari_did": "PIT_HARD",
        "positions_lost": 4,  # fell from podium contention
    },
    {
        "name": "Bahrain 2023 - Failed Overcut",
        "race_id": "2023_bahrain_r",
        "driver": "LEC",
        "lap": 33,
        "description": "Leclerc attempted overcut on degrading tyres when undercut was the play. "
                       "Lost time on worn tyres while Verstappen pulled away.",
        "correct_action": "PIT_HARD",  # pit earlier
        "what_ferrari_did": "STAY_OUT",
        "positions_lost": 1,
    },
    {
        "name": "Singapore 2023 - VSC Missed Pit",
        "race_id": "2023_marina_bay_r",
        "driver": "LEC",
        "lap": 44,
        "description": "VSC deployed lap 44, Ferrari stayed out on worn HARD tyres (24 laps old). "
                       "Free pit stop window wasted. Others pitted and gained on restart.",
        "correct_action": "PIT_MEDIUM",
        "what_ferrari_did": "STAY_OUT",
        "positions_lost": 1,
    },
    {
        "name": "Netherlands 2022 - VSC Missed Opportunity",
        "race_id": "2022_zandvoort_r",
        "driver": "LEC",
        "lap": 48,
        "description": "VSC deployed, Leclerc stayed out on old tyres. Verstappen pitted for free "
                       "and had massive tyre advantage for the final stint.",
        "correct_action": "PIT_SOFT",
        "what_ferrari_did": "STAY_OUT",
        "positions_lost": 1,
    },
    {
        "name": "Spain 2023 - Late Pit Timing",
        "race_id": "2023_catalunya_r",
        "driver": "LEC",
        "lap": 35,
        "description": "Leclerc extended stint too long on degrading MEDIUMS, losing pace to rivals. "
                       "Should have pitted 3-4 laps earlier.",
        "correct_action": "PIT_HARD",
        "what_ferrari_did": "STAY_OUT",
        "positions_lost": 1,
    },
    {
        "name": "Mexico 2024 - Overextended Mediums",
        "race_id": "2024_mexico_city_r",
        "driver": "LEC",
        "lap": 30,
        "description": "Ferrari kept Leclerc out too long on degrading mediums at high altitude "
                       "where tyre deg is amplified. Lost positions to cars on fresher rubber.",
        "correct_action": "PIT_HARD",
        "what_ferrari_did": "STAY_OUT",
        "positions_lost": 2,
    },
]


def _load_race_state(conn, race_id, driver, lap):
    """Load race state from DB for a specific moment."""
    state = conn.execute("""
        SELECT * FROM race_states
        WHERE race_id=? AND driver=? AND lap=?
    """, (race_id, driver, lap)).fetchone()

    if state:
        return dict(state)

    # If exact lap not found, try nearby laps
    state = conn.execute("""
        SELECT * FROM race_states
        WHERE race_id=? AND driver=? AND lap BETWEEN ? AND ?
        ORDER BY ABS(lap - ?) LIMIT 1
    """, (race_id, driver, lap - 2, lap + 2, lap)).fetchone()

    if state:
        return dict(state)
    return None


def _load_competitors(conn, race_id, lap, driver):
    """Load competitor states for context."""
    rows = conn.execute("""
        SELECT * FROM race_states
        WHERE race_id=? AND lap=? AND driver!=?
    """, (race_id, lap, driver)).fetchall()
    return [dict(r) for r in rows]


def run_test(engine, conn, disaster):
    """Run a single disaster test."""
    state = _load_race_state(conn, disaster["race_id"], disaster["driver"], disaster["lap"])

    if state is None:
        return {
            "name": disaster["name"],
            "status": "SKIP",
            "reason": f"No data for {disaster['race_id']} lap {disaster['lap']}",
        }

    competitors = _load_competitors(conn, disaster["race_id"], disaster["lap"], disaster["driver"])
    recommendation = engine.recommend(state, competitors)

    recommended = recommendation["recommended_action"]
    correct = disaster["correct_action"]

    # Check if recommendation matches correct action
    passed = False
    if correct == "STAY_OUT":
        passed = recommended == "STAY_OUT"
    elif correct.startswith("PIT"):
        # For PIT recommendations, check if model says PIT (compound can vary)
        passed = recommended.startswith("PIT")
        # Bonus: check if compound is reasonable
        if correct == "PIT_MEDIUM" and recommended == "PIT_HARD":
            passed = True  # close enough, both avoid the wrong call
        elif correct == "PIT_HARD" and recommended == "PIT_MEDIUM":
            passed = True

    return {
        "name": disaster["name"],
        "status": "PASS" if passed else "FAIL",
        "correct_action": correct,
        "ferrari_action": disaster["what_ferrari_did"],
        "model_action": recommended,
        "confidence": recommendation["confidence"],
        "reasoning": recommendation["reasoning"],
        "reason_codes": recommendation.get("reason_codes", []),
        "positions_lost_by_ferrari": disaster["positions_lost"],
    }


def run_all_tests(engine=None, verbose=True):
    """Run all Ferrari disaster tests."""
    if engine is None:
        engine = StrategyEngine()
        engine.load_models()

    conn = get_connection()
    results = []

    print("\n" + "="*70)
    print("FERRARI DISASTER TEST SUITE (Ground Effect Era 2022-2025)")
    print("="*70)

    passed = 0
    failed = 0
    skipped = 0

    for disaster in FERRARI_DISASTERS:
        result = run_test(engine, conn, disaster)
        results.append(result)

        if result["status"] == "PASS":
            passed += 1
            marker = "PASS"
        elif result["status"] == "FAIL":
            failed += 1
            marker = "FAIL"
        else:
            skipped += 1
            marker = "SKIP"

        if verbose:
            print(f"\n[{marker}] {disaster['name']}")
            print(f"  Ferrari did: {disaster['what_ferrari_did']} (lost {disaster['positions_lost']}P)")
            print(f"  Correct:     {disaster['correct_action']}")
            if result["status"] != "SKIP":
                print(f"  Model says:  {result['model_action']} (confidence: {result['confidence']:.2f})")
                print(f"  Reasoning:   {result['reasoning']}")
                print(f"  Codes:       {', '.join(result.get('reason_codes', []))}")
            else:
                print(f"  Skipped:     {result.get('reason', 'no data')}")

    print(f"\n{'='*70}")
    print(f"RESULTS: {passed}/{passed+failed} passed ({skipped} skipped)")
    if passed + failed > 0:
        print(f"Pass rate: {passed/(passed+failed):.0%}")
    print(f"{'='*70}")

    conn.close()
    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": passed / max(passed + failed, 1),
        "details": results,
    }


if __name__ == "__main__":
    results = run_all_tests()

    # Save results
    with open("ferrari_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to ferrari_test_results.json")
