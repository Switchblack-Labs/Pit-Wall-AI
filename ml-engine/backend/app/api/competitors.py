from fastapi import APIRouter, Depends

from app.schemas.competitors import CompetitorPayload
from app.dependencies import get_competitor_service
from app.services.competitor_service import CompetitorService

router = APIRouter(
    prefix="/api/competitors",
    tags=["competitors"]
)


@router.post("/")
def ingest_competitor(
    payload: CompetitorPayload,
    competitor_service: CompetitorService = Depends(get_competitor_service)
):
    competitor_service.update_competitor(payload)

    return {
        "status": "accepted",
        "car_id": payload.car_id
    }


@router.get("/")
def get_competitors(
    competitor_service: CompetitorService = Depends(get_competitor_service)
):
    return competitor_service.get_competitors()