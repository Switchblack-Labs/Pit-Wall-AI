from fastapi import APIRouter, Depends

from app.dependencies import get_explanation_service
from app.services.explanation_service import ExplanationService

router = APIRouter(
    prefix="/api/explain",
    tags=["explanation"]
)


@router.post("/")
async def explain(
    explanation_service: ExplanationService = Depends(
        get_explanation_service
    )
):
    return await explanation_service.explain_latest_strategy()