#!/usr/bin/env python3
"""
Master script: collects data, engineers features, trains models,
runs Ferrari disaster tests, and runs backtest.

Usage:
    python run_pipeline.py                    # full pipeline
    python run_pipeline.py --skip-collection  # skip FastF1 download
    python run_pipeline.py --tests-only       # just run tests
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.models.train import run_full_pipeline
from ml_engine.tests.ferrari_disasters import run_all_tests
from ml_engine.pipeline.backtest import BacktestRunner
from ml_engine.pipeline.strategy_engine import StrategyEngine
from ml_engine.data.schema import get_connection


def main():
    parser = argparse.ArgumentParser(description="Pit Wall AI ML Pipeline")
    parser.add_argument("--skip-collection", action="store_true")
    parser.add_argument("--tests-only", action="store_true")
    parser.add_argument("--backtest-year", type=int, default=2023)
    parser.add_argument("--seasons", nargs="+", type=int, default=None)
    args = parser.parse_args()

    if not args.tests_only:
        # Run full training pipeline
        results = run_full_pipeline(
            seasons=args.seasons,
            skip_collection=args.skip_collection
        )
        print(f"\nPipeline results: {results}")

    # Load engine with trained models
    engine = StrategyEngine()
    engine.load_models()

    # Run Ferrari disaster tests
    print("\n\nRunning Ferrari Disaster Test Suite...")
    test_results = run_all_tests(engine)

    # Run backtest
    print(f"\n\nRunning {args.backtest_year} backtest...")
    conn = get_connection()
    runner = BacktestRunner(engine)
    backtest_summary = runner.run_season(args.backtest_year, conn=conn)

    # Save all results
    output_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(output_dir, exist_ok=True)

    runner.save_results(os.path.join(output_dir, f"backtest_{args.backtest_year}.json"))

    import json
    with open(os.path.join(output_dir, "ferrari_tests.json"), "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump({
            "ferrari_tests": {
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "skipped": test_results["skipped"],
                "pass_rate": test_results["pass_rate"],
            },
            "backtest": backtest_summary,
        }, f, indent=2)

    print(f"\nAll results saved to {output_dir}/")

    conn.close()


if __name__ == "__main__":
    main()
