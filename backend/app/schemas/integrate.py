"""
Integration-facing schemas for the Pit Wall AI strategy API.

These are the STABLE contract your teammate builds the frontend against.
They do not change when the ML models are retrained in the background —
only the numbers in the response change, never the shape.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Competitor(BaseModel):
    """A rival car near you. Used for undercut/overcut logic."""
    position: int = Field(..., description="Track position, e.g. 4")
    compound: str = Field("MEDIUM", description="SOFT | MEDIUM | HARD | INTERMEDIATE | WET")
    tyre_life: int = Field(10, description="Laps on current tyre")


class RaceStateInput(BaseModel):
    """
    Everything the engine needs to make a pit call.
    All fields optional with sane defaults so the UI can send a partial state.
    """
    circuit: str = Field("bahrain", description="Canonical circuit name, e.g. bahrain, monaco, monza")
    compound: str = Field("MEDIUM", description="Current tyre: SOFT | MEDIUM | HARD | INTERMEDIATE | WET")
    tyre_life: int = Field(15, description="Laps on the current tyre")
    laps_remaining: int = Field(25, description="Laps left in the race")
    total_laps: int = Field(57, description="Total race laps")
    position: int = Field(5, description="Current track position")
    gap_ahead_s: Optional[float] = Field(2.0, description="Seconds to car ahead")
    gap_behind_s: Optional[float] = Field(3.0, description="Seconds to car behind")
    pit_loss_s: float = Field(22.0, description="Time lost for a pit stop at this circuit")
    track_temp: Optional[float] = Field(35.0, description="Track temperature °C")
    track_status: str = Field("1", description="1=green 2=yellow 4=SafetyCar 5=red 6=VSC")
    compounds_used: str = Field("SOFT", description="Comma list of compounds already used this race")
    stops_made: int = Field(1, description="Pit stops made so far")
    deg_rate: Optional[float] = Field(None, description="Optional measured deg rate (s/lap); engine predicts if omitted")
    competitors: Optional[List[Competitor]] = Field(None, description="Nearby rivals for undercut analysis")


class FullRecommendation(BaseModel):
    """What the API returns. recommended_action is the machine-readable call;
    explanation is the Granite natural-language pit-wall message."""
    recommended_action: str = Field(..., description="PIT_SOFT | PIT_MEDIUM | PIT_HARD | STAY_OUT")
    confidence: float = Field(..., description="0.0–1.0")
    risk_level: str = Field(..., description="low | medium | high")
    reason_codes: List[str] = Field(..., description="e.g. HIGH_DEGRADATION, UNDERCUT_VIABLE, SAFETY_CAR_PIT_WINDOW")
    explanation: str = Field(..., description="Granite-generated natural-language advice for the pit wall")
