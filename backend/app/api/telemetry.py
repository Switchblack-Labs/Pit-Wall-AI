from fastapi import APIRouter, Depends

from app.schemas.telemetry import TelemetryPayload
from app.dependencies import get_telemetry_service
from app.services.telemetry_service import TelemetryService

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