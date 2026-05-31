"""
Backtesting pipeline. Runs the strategy engine on historical race data
and computes agreement rate, outcome rate, and projected position delta.
"""
import os
import sys
import json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_engine.data.schema import get_connection
from ml_engine.pipeline.strategy_engine import StrategyEngine
from ml_engine.config import FERRARI_DRIVERS


class BacktestRunner:
    def __init__(self, engine=None):
        self.engine = engine or StrategyEngine()
        self.results = []

    def run_race(self, conn, race_id, drivers=None):
        """Run backtest on a single race for specified drivers."""
        race = conn.execute("SELECT * FROM races WHERE race_id=?", (race_id,)).fetchone()
        if not race:
            return []

        if drivers is None:
            drivers = [r["driver"] for r in conn.execute(
                "SELECT DISTINCT driver FROM race_states WHERE race_id=?", (race_id,)
            ).fetchall()]

        race_results = []
        for driver in drivers:
            states = conn.execute("""
                SELECT * FROM race_states
                WHERE race_id=? AND driver=?
                AND lap_time_s IS NOT NULL
                ORDER BY lap
            """, (race_id, driver)).fetchall()

            for state_row in states:
                state = dict(state_row)

                # Skip pit laps, SC laps with no useful decision
                if state.get("laps_remaining", 0) <= 2:
                    continue

                # Get competitors on this lap
                competitors = [
                    dict(c) for c in conn.execute("""
                        SELECT * FROM race_states
                        WHERE race_id=? AND lap=? AND driver!=?
                    """, (race_id, state["lap"], driver)).fetchall()
                ]

                recommendation = self.engine.recommend(state, competitors)

                # Compare with actual decision
                actual = state.get("decision_made", "STAY_OUT")
                recommended = recommendation["recommended_action"]

                # Normalize for comparison
                rec_action = "PIT" if recommended.startswith("PIT") else "STAY_OUT"
                agrees = (rec_action == actual)

                # Outcome: did the actual decision work?
                outcome = state.get("outcome_rating", "neutral")

                result = {
                    "race_id": race_id,
                    "circuit": state.get("circuit"),
                    "lap": state["lap"],
                    "driver": driver,
                    "position": state.get("position"),
                    "actual_decision": actual,
                    "recommended_action": recommended,
                    "confidence": recommendation["confidence"],
                    "agrees": agrees,
                    "actual_outcome": outcome,
                    "model_was_right": None,
                    "reason_codes": recommendation.get("reason_codes", []),
                    "reasoning": recommendation.get("reasoning", ""),
                    "positions_delta_5": state.get("positions_delta_5"),
                    "positions_delta_10": state.get("positions_delta_10"),
                }

                # Model was right if: agreed and outcome good, or disagreed and outcome bad
                if agrees:
                    result["model_was_right"] = outcome in ("good", "neutral")
                else:
                    result["model_was_right"] = outcome == "bad"

                race_results.append(result)

        self.results.extend(race_results)
        return race_results

    def run_season(self, year, team="Ferrari", conn=None):
        """Run backtest on all races for a team in a given season."""
        if conn is None:
            conn = get_connection()

        drivers = FERRARI_DRIVERS.get(year, ["LEC", "SAI"])

        races = conn.execute(
            "SELECT race_id FROM races WHERE year=? ORDER BY date", (year,)
        ).fetchall()

        print(f"\nBacktesting {year} season for {team} ({', '.join(drivers)})")
        print(f"{'='*60}")

        for race in races:
            race_id = race["race_id"]
            results = self.run_race(conn, race_id, drivers)
            n_disagree = sum(1 for r in results if not r["agrees"])
            n_right = sum(1 for r in results if r.get("model_was_right"))
            print(f"  {race_id}: {len(results)} decisions, {n_disagree} disagreements, {n_right} correct")

        return self.compute_summary()

    def run_all(self, conn=None):
        """Run backtest on all seasons."""
        if conn is None:
            conn = get_connection()

        for year in [2022, 2023, 2024, 2025]:
            self.run_season(year, conn=conn)

        return self.compute_summary()

    def compute_summary(self):
        """Compute summary statistics from all backtest results."""
        if not self.results:
            return {"error": "No results"}

        total = len(self.results)
        agrees = sum(1 for r in self.results if r["agrees"])
        disagrees = total - agrees

        # When model disagrees, was it right?
        disagree_results = [r for r in self.results if not r["agrees"]]
        model_right_on_disagree = sum(1 for r in disagree_results if r.get("model_was_right"))

        # Position deltas when model disagrees
        disagree_with_delta = [r for r in disagree_results if r["positions_delta_5"] is not None]
        avg_pos_delta = 0
        if disagree_with_delta:
            avg_pos_delta = sum(r["positions_delta_5"] for r in disagree_with_delta) / len(disagree_with_delta)

        # Per-race summary
        race_summaries = defaultdict(lambda: {"total": 0, "agrees": 0, "model_right": 0})
        for r in self.results:
            rid = r["race_id"]
            race_summaries[rid]["total"] += 1
            if r["agrees"]:
                race_summaries[rid]["agrees"] += 1
            if r.get("model_was_right"):
                race_summaries[rid]["model_right"] += 1

        summary = {
            "total_decisions": total,
            "agreement_rate": agrees / total if total else 0,
            "disagreement_rate": disagrees / total if total else 0,
            "n_disagreements": disagrees,
            "model_right_on_disagree": model_right_on_disagree,
            "model_right_rate_on_disagree": (
                model_right_on_disagree / disagrees if disagrees else 0
            ),
            "avg_position_delta_on_disagree": avg_pos_delta,
            "n_races": len(race_summaries),
        }

        print(f"\n{'='*60}")
        print("BACKTEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total decisions analyzed: {total}")
        print(f"Agreement rate:          {summary['agreement_rate']:.1%}")
        print(f"Disagreements:           {disagrees}")
        print(f"Model right when disagrees: {model_right_on_disagree}/{disagrees} "
              f"({summary['model_right_rate_on_disagree']:.1%})")
        print(f"Avg position delta (disagree): {avg_pos_delta:+.2f}")

        return summary

    def save_results(self, path):
        """Save detailed results to JSON."""
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

    def get_worst_calls(self, n=10):
        """Get the worst actual decisions (model disagreed and was right)."""
        bad = [r for r in self.results
               if not r["agrees"] and r.get("model_was_right")
               and r.get("positions_delta_5") is not None]
        bad.sort(key=lambda x: x["positions_delta_5"])
        return bad[:n]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--output", type=str, default="backtest_results.json")
    args = parser.parse_args()

    engine = StrategyEngine()
    engine.load_models()
    runner = BacktestRunner(engine)
    summary = runner.run_season(args.year)
    runner.save_results(args.output)
    print(f"\nDetailed results saved to {args.output}")
