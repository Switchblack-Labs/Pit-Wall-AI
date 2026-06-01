from pydantic import BaseModel


class SimulationRequest(BaseModel):
    scenario_type: str
    laps_until_action: int


class SimulationResult(BaseModel):
    projected_position: int
    projected_gap: float
    projected_risk: str