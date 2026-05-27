from pydantic import BaseModel, Field


class CompetitorPayload(BaseModel):
    car_id: str
    position: int = Field(..., ge=1)
    gap: float
    pit_status: bool
    pace_delta: float
    tire_wear: float = Field(..., ge=0, le=1)