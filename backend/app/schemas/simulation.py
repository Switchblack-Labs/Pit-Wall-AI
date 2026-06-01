from typing import Optional
from pydantic import BaseModel, Field


class SimulationContext(BaseModel):
    """Optional race state the frontend can pass through to make the projection
    reflect the actual race situation instead of generic defaults."""
    circuit: Optional[str] = None
    lap: Optional[int] = None
    total_laps: Optional[int] = None
    position: Optional[int] = None
    gap_s: Optional[float] = Field(None, description="Gap to leader/reference")
    gap_ahead_s: Optional[float] = None
    gap_behind_s: Optional[float] = None
    tyre_age_laps: Optional[int] = None
    compound: Optional[str] = None
    pit_loss_s: Optional[float] = None
    track_temp: Optional[float] = None
    track_status: Optional[str] = None
    stops_made: Optional[int] = None
    compounds_used: Optional[str] = None


class SimulationRequest(BaseModel):
    scenario_type: str
    laps_until_action: int
    context: Optional[SimulationContext] = None


class SimulationResult(BaseModel):
    projected_position: int
    projected_gap: float
    projected_risk: str
