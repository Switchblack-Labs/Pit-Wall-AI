# Pit Wall AI — ML Engine Handoff

## Project
F1 race strategy engine for IBM SkillsBuild AI Builders Challenge.
- **Repo**: `Switchblack-Labs/Pit-Wall-AI` on GitHub
- **Branch**: `ml-engine` (all ML code pushed here)
- **Deadline**: May 31, 2026

## Remote Machine
- **SSH**: `ssh devang@100.124.177.107` (key-based, no password)
- **GPU**: RTX 4070 (CUDA), Linux, Python 3.12
- **Virtualenv**: `source ~/pit-wall-env/bin/activate`
- **Working dir**: `~/pit-wall-ai/`
- **DO NOT run compute on local Mac** — everything runs on remote

## What's Running Right Now

A background process is collecting remaining F1 data via FastF1 API:

```
PID 251706 on remote (parent: bash resume_collection.sh)
```

**Status when last checked**: 2024 season at 23/24 races (Abu Dhabi pending, waiting on FastF1 rate limit ~500 calls/hour). After Abu Dhabi 2024, it collects all 24 races of 2025.

**After collection finishes, `resume_collection.sh` automatically**:
1. Re-runs feature engineering on ALL data
2. Re-fits degradation curves
3. Retrains XGBoost deg predictor + LightGBM overtake model
4. Re-runs Ferrari Disaster Test Suite
5. Prints results

**Check progress**:
```bash
ssh devang@100.124.177.107 "tail -20 ~/pit-wall-ai/resume_output.log"
```

**Check if process is still alive**:
```bash
ssh devang@100.124.177.107 "ps aux | grep python | grep -v grep"
```

## What's Done

### Data Pipeline
- **Collector** (`ml_engine/data/collector.py`): FastF1 → SQLite with rate limiting, circuit name canonicalization
- **Schema** (`ml_engine/data/schema.py`): 6 tables — races, laps, weather, pit_stops, stints, race_states
- **Features** (`ml_engine/data/features.py`): 35 features per driver per lap (gaps, deg rate, sector trends, undercut windows, outcomes)
- **DB location on remote**: `~/pit-wall-ai/ml_engine/data/f1_data.db`
- **Current data**: 67 races (2022: 22, 2023: 22, 2024: 23), ~73K laps, ~47K race states

### Math Engine
- **Degradation** (`ml_engine/math_engine/degradation.py`): Power-fit curves per (circuit, compound) via scipy
- **Undercut/Overcut** (`ml_engine/math_engine/undercut.py`): Lap-by-lap pace delta simulation
- **Safety Car** (`ml_engine/math_engine/safety_car.py`): 6-factor scoring (tyre life, position, gap, laps remaining, compound rule, field bunching)
- **Overtake** (`ml_engine/math_engine/overtake.py`): Circuit-specific base rates + gap/tyre/DRS modifiers
- **Projection** (`ml_engine/math_engine/projection.py`): Full race-forward simulation

### ML Models
- **Deg Predictor** (`ml_engine/models/deg_predictor.py`): XGBoost GPU, 8 features → lap_time_delta_vs_fresh. RMSE 4.51s vs 5.62s baseline (19.8% improvement)
- **Overtake Model** (`ml_engine/models/overtake_model.py`): LightGBM, 12 features → binary overtake. AUC 0.82, accuracy 73.5%
- **Saved models**: `ml_engine/models/saved/` (deg_predictor.pkl, overtake_model.pkl, deg_curves.json, encoders, meta)

### Strategy Engine
- **Core** (`ml_engine/pipeline/strategy_engine.py`): Combines math + ML → decision with confidence, risk level, reason codes, reasoning text, projections
- **Forced pit logic**: deg > 0.2 AND near cliff, OR deg > 0.15 AND total_deg_loss > pit_loss * 0.8
- **SC override**: `_best_sc_compound()` evaluates ALL compounds for long stints
- **Late race guard**: won't pit in last 5 laps unless critical

### Ferrari Disaster Test Suite
- **File**: `ml_engine/tests/ferrari_disasters.py`
- **Result**: 6/7 passed (86%), 1 skipped (Mexico 2024 — no data yet, will pass after collection)
- **Tests**: Monaco 2022 ✅, Britain 2022 ✅, Hungary 2022 ✅, Bahrain 2023 ❌ (marginal), Singapore 2023 ✅, Netherlands 2022 ✅, Spain 2023 ✅

### Backend Integration
- **`backend/app/engine/strategy_engine.py`**: Drop-in replacement, returns `StrategyRecommendation` Pydantic model
- **`backend/app/engine/scenario_engine.py`**: Drop-in replacement, returns `SimulationResult` Pydantic model
- **`ml_engine/integration.py`**: Shared engine singleton (models loaded once)
- **Integration test**: `ml_engine/tests/test_integration.py` — ALL PASSING

### Backtests
- Results in `ml_engine/results/backtest_2022.json` and `backtest_2023.json`

## What Needs To Be Done

### 1. Monitor & Verify Collection + Retrain (PRIORITY)
The `resume_collection.sh` process should finish on its own. When it does:
- Check `~/pit-wall-ai/resume_output.log` for final results
- Verify Mexico 2024 Ferrari test now passes (was SKIP due to no data)
- Download updated models from remote: `scp devang@100.124.177.107:~/pit-wall-ai/ml_engine/models/saved/* /tmp/Pit-Wall-AI/ml_engine/models/saved/`
- Download updated test results: `scp devang@100.124.177.107:~/pit-wall-ai/ferrari_test_results.json /tmp/Pit-Wall-AI/ml_engine/results/`
- Commit and push updated models to `ml-engine` branch

If the process died (rate limit issues, SSH timeout), restart:
```bash
ssh devang@100.124.177.107 "cd ~/pit-wall-ai && source ~/pit-wall-env/bin/activate && nohup bash resume_collection.sh > resume_output.log 2>&1 &"
```

### 2. Fix Bahrain 2023 Test (Nice-to-Have)
The one failing test: Bahrain 2023 lap 33 — model says STAY_OUT at 0.50 confidence, correct is PIT_HARD. The engine flags HIGH_DEGRADATION but the projection doesn't strongly favor pitting. After retrain with more data this may self-correct. If not, consider tuning `force_pit` thresholds in `strategy_engine.py`.

### 3. Improve Scenario Engine
`simulate_strategy()` currently uses a generic default state. Should accept actual race state from the backend. The `SimulationService` only passes `scenario_type` and `laps_until_action` — either:
- Extend the schema to pass full state, OR
- Have the engine pull current state from a shared store

### 4. Team Radio Transcription (Stretch)
User mentioned as a stretch goal — transcribe rival team radios for pit strategy intel. Not started.

## Key Files Quick Reference

```
ml_engine/
├── config.py                    # DB paths, seasons, circuit aliases, compound encoding
├── integration.py               # Shared engine singleton for backend
├── run_pipeline.py              # Master CLI: --skip-collection, --tests-only, --backtest-year
├── data/
│   ├── schema.py                # SQLite schema + get_connection()
│   ├── collector.py             # FastF1 → SQLite with rate limiting
│   ├── features.py              # 35-feature engineering per lap
│   └── migrate_circuits.py      # One-time circuit name fix
├── math_engine/
│   ├── degradation.py           # Scipy curve fit + prediction
│   ├── undercut.py              # Undercut/overcut viability
│   ├── safety_car.py            # SC/VSC pit advisor
│   ├── overtake.py              # Overtake probability
│   └── projection.py            # Race-forward simulation
├── models/
│   ├── deg_predictor.py         # XGBoost tyre deg (GPU)
│   ├── overtake_model.py        # LightGBM overtake
│   ├── train.py                 # Full training orchestrator
│   └── saved/                   # Trained model artifacts
├── pipeline/
│   ├── strategy_engine.py       # Main engine: math + ML → decision
│   └── backtest.py              # Season-level backtesting
├── tests/
│   ├── ferrari_disasters.py     # 8 ground-effect era test cases
│   └── test_integration.py      # Backend smoke test
└── results/                     # Backtest & test result JSONs

backend/app/engine/
├── strategy_engine.py           # DROP-IN: returns StrategyRecommendation
└── scenario_engine.py           # DROP-IN: returns SimulationResult
```

## Remote Machine State
- **Virtualenv packages**: fastf1, xgboost (GPU), lightgbm, scipy, numpy, pandas, scikit-learn, pydantic
- **FastF1 cache**: `~/pit-wall-ai/ml_engine/data/fastf1_cache/` (saves re-downloading)
- **SQLite DB**: `~/pit-wall-ai/ml_engine/data/f1_data.db` (~100MB+)
- **No sqlite3 CLI** on remote — use Python to query

## Running Tests Manually
```bash
ssh devang@100.124.177.107
source ~/pit-wall-env/bin/activate
cd ~/pit-wall-ai

# Ferrari tests
python3 ml_engine/tests/ferrari_disasters.py

# Integration test
python3 ml_engine/tests/test_integration.py

# Full pipeline (skip data collection)
python3 ml_engine/run_pipeline.py --skip-collection --backtest-year 2023

# Retrain only
python3 -c "
import sys; sys.path.insert(0, '.')
from ml_engine.models.train import run_full_pipeline
run_full_pipeline(skip_collection=True)
"
```
