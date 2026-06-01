"""Endpoints that surface ml_engine + orchestration artifacts to the frontend.

* GET /api/v1/disasters       - Ferrari disaster catalogue from ml_engine/tests
* GET /api/v1/backtests       - committed season-level backtest results
* GET /api/v1/ferrari-results - committed Ferrari-test-suite results
* GET /api/orchestration/flows - list of orchestration workflows
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["extras"])

_ML_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ml_engine",
)
_RESULTS_DIR = os.path.join(_ML_ROOT, "results")


from pydantic import BaseModel
from app.schemas.simulation import SimulationContext


class ScenariosRequest(BaseModel):
    context: SimulationContext


@router.post("/api/v1/scenarios")
def project_scenarios(req: ScenariosRequest) -> List[Dict[str, Any]]:
    """Run the ml_engine race projector for every possible decision and return
    per-lap projections so the frontend can render real branching curves.
    """
    from ml_engine.integration import get_engine

    ctx = req.context.model_dump(exclude_none=True)

    if "tyre_age_laps" in ctx:
        ctx["tyre_life"] = ctx.pop("tyre_age_laps")
    if "lap" in ctx and "total_laps" in ctx:
        ctx.setdefault("laps_remaining", max(1, ctx["total_laps"] - ctx["lap"]))
    ctx.pop("lap", None)
    compound_map = {"S": "SOFT", "M": "MEDIUM", "H": "HARD",
                    "I": "INTERMEDIATE", "W": "WET"}
    if ctx.get("compound") in compound_map:
        ctx["compound"] = compound_map[ctx["compound"]]
    if "gap_s" in ctx:
        ctx.setdefault("gap_to_leader_s", ctx.pop("gap_s"))

    engine = get_engine()

    decisions = ["STAY_OUT", "PIT_SOFT", "PIT_MEDIUM", "PIT_HARD"]
    out: List[Dict[str, Any]] = []
    baseline_time = None
    for d in decisions:
        proj = engine.projector.project(ctx, d)
        if d == "STAY_OUT":
            baseline_time = proj["projected_total_time"]
        out.append({
            "decision": d,
            "projected_position": proj["projected_position"],
            "projected_total_time": proj["projected_total_time"],
            "projected_lap_times": proj["projected_lap_times"],
            "avg_pace": proj["avg_projected_pace"],
        })

    stay_out = next(s for s in out if s["decision"] == "STAY_OUT")
    stay_cum = []
    acc = 0.0
    for lt in stay_out["projected_lap_times"]:
        acc += lt
        stay_cum.append(acc)

    for s in out:
        acc = 0.0
        points = []
        for i, lt in enumerate(s["projected_lap_times"]):
            acc += lt
            ref = stay_cum[i] if i < len(stay_cum) else stay_cum[-1] if stay_cum else 0
            points.append({"lap_offset": i + 1, "gap_s": round(acc - ref, 3)})
        s["points"] = points
        s["net_gain_s"] = round(
            (baseline_time - s["projected_total_time"]) if baseline_time is not None else 0.0,
            2,
        )

    return out


@router.get("/api/v1/disasters")
def list_disasters() -> List[Dict[str, Any]]:
    """Return the FERRARI_DISASTERS list from ml_engine/tests/ferrari_disasters.py
    so the frontend has a single source of truth."""
    from ml_engine.tests.ferrari_disasters import FERRARI_DISASTERS
    return FERRARI_DISASTERS


@router.get("/api/v1/ferrari-results")
def ferrari_results() -> Dict[str, Any]:
    """Last-committed Ferrari disaster test-suite run."""
    path = os.path.join(_RESULTS_DIR, "ferrari_test_results.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="ferrari_test_results.json missing")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/api/v1/backtests")
def list_backtests() -> Dict[str, Any]:
    """All backtest_YEAR.json files in ml_engine/results, indexed by year."""
    if not os.path.isdir(_RESULTS_DIR):
        raise HTTPException(status_code=404, detail="ml_engine/results missing")
    out: Dict[str, Any] = {}
    for fname in sorted(os.listdir(_RESULTS_DIR)):
        if fname.startswith("backtest_") and fname.endswith(".json"):
            year = fname[len("backtest_"):-len(".json")]
            with open(os.path.join(_RESULTS_DIR, fname), "r", encoding="utf-8") as f:
                out[year] = json.load(f)
    return out


@router.get("/api/v1/backtests/{year}")
def backtest_year(year: str) -> List[Dict[str, Any]]:
    """One year's backtest results."""
    path = os.path.join(_RESULTS_DIR, f"backtest_{year}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"backtest_{year}.json missing")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/api/orchestration/flows")
def list_flows() -> List[Dict[str, Any]]:
    """Catalogue of orchestration workflows + their status."""
    from app.orchestration.fia_workflow import FiaWorkflow, FLOW_ID as FIA_FLOW_ID
    from app.orchestration.explainability_workflow import (
        ExplainabilityWorkflow,
        FLOW_ID as EXPL_FLOW_ID,
    )

    fia = FiaWorkflow()
    expl = ExplainabilityWorkflow()
    langflow_enabled = fia._langflow.is_enabled()

    return [
        {
            "id": FIA_FLOW_ID,
            "name": "FIA Regulations RAG",
            "description": "Question > Retriever > Context Builder > Granite > Answer.",
            "steps": ["question", "retriever", "context_builder", "granite", "answer"],
            "langflow_enabled": langflow_enabled,
            "endpoint": "/api/rag/query",
        },
        {
            "id": EXPL_FLOW_ID,
            "name": "Strategy Explainability",
            "description": "Structured pit call > Granite race-engineer prompt > Natural-language explanation.",
            "steps": ["recommendation", "prompt_builder", "granite", "explanation"],
            "langflow_enabled": langflow_enabled,
            "endpoint": "/api/explain/",
        },
    ]
