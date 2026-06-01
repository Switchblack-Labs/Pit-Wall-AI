from fastapi import APIRouter, Depends, HTTPException

from app.schemas.telemetry import TelemetryPayload
from app.dependencies import get_telemetry_service, get_race_state_service
from app.services.telemetry_service import TelemetryService
from app.services.race_state_service import RaceStateService

router = APIRouter(
    prefix="/api/telemetry",
    tags=["telemetry"]
)


@router.post("/")
async def ingest_telemetry(
    payload: TelemetryPayload,
    telemetry_service: TelemetryService = Depends(get_telemetry_service)
):
    return await telemetry_service.ingest(payload)


@router.get("/")
def current_telemetry(
    race_state_service: RaceStateService = Depends(get_race_state_service),
):
    telemetry = race_state_service.get_state().get("telemetry")
    if not telemetry:
        raise HTTPException(status_code=404, detail="no telemetry ingested yet")
    return telemetry