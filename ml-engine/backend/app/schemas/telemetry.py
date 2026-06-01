from datetime import datetime
from pydantic import BaseModel, Field


class TelemetryPayload(BaseModel):
    speed: float = Field(..., ge=0)
    rpm: int = Field(..., ge=0)
    gear: int
    throttle: float = Field(..., ge=0, le=1)
    brake: float = Field(..., ge=0, le=1)
    steering_angle: float
    track_position: float
    lap: int = Field(..., ge=0)
    fuel: float = Field(..., ge=0)
    tire_wear: float = Field(..., ge=0, le=1)
    timestamp: datetime