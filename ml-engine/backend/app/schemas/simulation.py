from typing import Optional
from pydantic import BaseModel


class SimulationRequest(BaseModel):
    scenario_type: str
    laps_until_action: int

    # Optional real race state. When provided, the simulator projects from the
    # actual situation instead of a hardcoded default. All optional so existing
    # callers that only send scenario_type + laps_until_action still work.
    circuit: Optional[str] = None
    compound: Optional[str] = None
    tyre_life: Optional[int] = None
    laps_remaining: Optional[int] = None
    total_laps: Optional[int] = None
    position: Optional[int] = None
    gap_ahead_s: Optional[float] = None
    gap_behind_s: Optional[float] = None
    gap_to_leader_s: Optional[float] = None
    pit_loss_s: Optional[float] = None
    track_temp: Optional[float] = None
    compounds_used: Optional[str] = None
    stops_made: Optional[int] = None
    track_status: Optional[str] = None


class SimulationResult(BaseModel):
    projected_position: int
    projected_gap: float
    projected_risk: str