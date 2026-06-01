from fastapi import APIRouter

from app.adapters.mock_adapter import MockTelemetryAdapter

router = APIRouter(
    prefix="/api/mock",
    tags=["mock"]
)

adapter = MockTelemetryAdapter()


@router.get("/telemetry")
def mock_telemetry():
    return adapter.normalize().model_dump(mode="json")