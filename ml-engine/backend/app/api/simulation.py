from fastapi import APIRouter, Depends

from app.schemas.simulation import (
    SimulationRequest
)
from app.dependencies import get_simulation_service
from app.services.simulation_service import SimulationService

router = APIRouter(
    prefix="/api/simulate",
    tags=["simulation"]
)


@router.post("/")
async def simulate(
    payload: SimulationRequest,
    simulation_service: SimulationService = Depends(
        get_simulation_service
    )
):
    return await simulation_service.run_simulation(
        payload
    )