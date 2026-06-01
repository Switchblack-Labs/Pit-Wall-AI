"""
Master training script. Runs on the GPU machine.
Collects data, engineers features, fits math models, trains ML models.
"""
import os
import sys
import time

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_engine.data.schema import init_db, get_connection
from ml_engine.data.collector import collect_all, setup_cache
from ml_engine.data.features import engineer_all
from ml_engine.math_engine.degradation import DegradationModel
from ml_engine.math_engine.overtake import OvertakeModel
from ml_engine.models.deg_predictor import DegPredictor
from ml_engine.models.overtake_model import OvertakePredictor
from ml_engine.config import MODEL_DIR, SEASONS


def run_full_pipeline(seasons=None, skip_collection=False):
    """Run the full data → features → math → ML pipeline."""
    if seasons is None:
        seasons = SEASONS

    os.makedirs(MODEL_DIR, exist_ok=True)
    start = time.time()

    # Step 1: Data collection
    if not skip_collection:
        print("\n" + "="*60)
        print("STEP 1: Collecting FastF1 data")
        print("="*60)
        collect_all(seasons)
    else:
        print("Skipping data collection (using existing DB)")

    # Step 2: Feature engineering
    print("\n" + "="*60)
    print("STEP 2: Engineering features")
    print("="*60)
    engineer_all()

    conn = get_connection()

    # Stats
    n_races = conn.execute("SELECT COUNT(*) FROM races").fetchone()[0]
    n_laps = conn.execute("SELECT COUNT(*) FROM laps").fetchone()[0]
    n_states = conn.execute("SELECT COUNT(*) FROM race_states").fetchone()[0]
    n_ferrari = conn.execute(
        "SELECT COUNT(*) FROM race_states WHERE team LIKE '%Ferrari%'"
    ).fetchone()[0]

    print(f"\nData summary:")
    print(f"  Races:        {n_races}")
    print(f"  Lap records:  {n_laps}")
    print(f"  Race states:  {n_states}")
    print(f"  Ferrari:      {n_ferrari}")

    # Step 3: Fit math models
    print("\n" + "="*60)
    print("STEP 3: Fitting degradation curves (scipy)")
    print("="*60)
    deg_model = DegradationModel()
    n_curves = deg_model.fit_all(conn)
    print(f"  Fitted {n_curves} (circuit, compound) curves")
    deg_model.save(os.path.join(MODEL_DIR, "deg_curves.json"))

    # Update overtake rates from data
    print("\n  Updating overtake rates from data...")
    overtake_model = OvertakeModel()
    overtake_model.fit_from_data(conn)
    print(f"  Updated rates for {len(overtake_model.circuit_rates)} circuits")

    # Step 4: Train ML models
    print("\n" + "="*60)
    print("STEP 4: Training ML deg predictor (XGBoost)")
    print("="*60)
    deg_predictor = DegPredictor()
    deg_beats = deg_predictor.train(conn)
    if deg_beats:
        deg_predictor.save()
        print("  Saved ML deg predictor (beats baseline)")
    else:
        print("  ML deg predictor does NOT beat scipy baseline - using curves only")

    print("\n" + "="*60)
    print("STEP 5: Training overtake predictor (LightGBM)")
    print("="*60)
    overtake_predictor = OvertakePredictor()
    overtake_beats = overtake_predictor.train(conn)
    if overtake_beats:
        overtake_predictor.save()
        overtake_model.set_ml_model(overtake_predictor.model)
        print("  Saved ML overtake model (beats baseline)")
    else:
        print("  ML overtake model does NOT beat hardcoded rates - using rates only")

    conn.close()

    elapsed = time.time() - start
    print("\n" + "="*60)
    print(f"PIPELINE COMPLETE in {elapsed/60:.1f} minutes")
    print("="*60)
    print(f"\nModels saved to: {MODEL_DIR}")
    print(f"  deg_curves.json       - scipy degradation curves")
    if deg_beats:
        print(f"  deg_predictor.pkl     - XGBoost deg model")
    if overtake_beats:
        print(f"  overtake_model.pkl    - LightGBM overtake model")

    return {
        "n_races": n_races,
        "n_states": n_states,
        "deg_beats_baseline": deg_beats,
        "overtake_beats_baseline": overtake_beats,
        "elapsed_min": elapsed / 60,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-collection", action="store_true",
                        help="Skip FastF1 data collection, use existing DB")
    parser.add_argument("--seasons", nargs="+", type=int, default=None,
                        help="Seasons to collect (default: 2022-2025)")
    args = parser.parse_args()

    run_full_pipeline(seasons=args.seasons, skip_collection=args.skip_collection)
