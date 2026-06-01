from fastapi import APIRouter, Depends

from app.dependencies import get_strategy_service
from app.services.strategy_service import StrategyService

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"]
)


@router.post("/recommend")
async def recommend(
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    return await strategy_service.generate_recommendation()