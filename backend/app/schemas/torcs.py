"""TORCS telemetry schemas.

These model the *TORCS-format* stream produced either by the built-in simulated
source or, in future, a live TORCS/SCR bridge. They are additive and separate
from :class:`app.schemas.telemetry.TelemetryPayload` (the backend's canonical
telemetry contract) — `app/integrations/torcs/ingest.py` maps from this richer
TORCS shape down to the existing backend schemas so nothing downstream changes.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TorcsCompetitorGap(BaseModel):
    """A rival car's relative position as seen from TORCS opponent sensors."""

    car_id: str
    position: int = Field(..., ge=1)
    gap: float  # seconds; negative = ahead, positive = behind
    pit_status: bool = False
    pace_delta: float = 0.0
    tire_wear: float = Field(0.0, ge=0, le=1)


class TorcsTelemetry(BaseModel):
    """A single TORCS telemetry frame.

    Mirrors the SCR sensor model (speed, rpm, gear, fuel, trackPos ...) plus
    derived race fields (sector times, race events, competitor gaps) that a
    race engineer needs.
    """

    # --- Core car sensors ---
    speed: float = Field(..., ge=0)          # km/h
    rpm: int = Field(..., ge=0)
    gear: int
    throttle: float = Field(..., ge=0, le=1)
    brake: float = Field(..., ge=0, le=1)
    steering: float = Field(0.0)             # SCR "steer" sensor, [-1, 1]
    track_position: float = Field(..., ge=-1, le=1)  # SCR "trackPos"
    lap: int = Field(..., ge=0)
    fuel: float = Field(..., ge=0)           # litres/kg
    tire_wear: float = Field(..., ge=0, le=1)

    # --- Derived race context ---
    cur_lap_time: float = Field(0.0, ge=0)
    last_lap_time: Optional[float] = Field(None, ge=0)
    sector_times: List[float] = Field(default_factory=list)
    race_events: List[str] = Field(default_factory=list)  # e.g. ["SC"], ["PIT"]
    competitor_gaps: List[TorcsCompetitorGap] = Field(default_factory=list)

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def to_adapter_dict(self) -> dict:
        """Shape this frame for the existing ``TORCSTelemetryAdapter``.

        The legacy adapter (``app/adapters/torcs_adapter.py``) consumes a dict
        with a ``"steering"`` key; we reuse it rather than duplicating the
        mapping to ``TelemetryPayload``.
        """
        return {
            "speed": self.speed,
            "rpm": self.rpm,
            "gear": self.gear,
            "throttle": self.throttle,
            "brake": self.brake,
            "steering": self.steering,
            "track_position": self.track_position,
            "lap": self.lap,
            "fuel": self.fuel,
            "tire_wear": self.tire_wear,
            "timestamp": self.timestamp,
        }
