import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_torcs_service
from app.services.torcs_service import TorcsService

router = APIRouter(
    prefix="/api/torcs",
    tags=["torcs"]
)


class TorcsStartRequest(BaseModel):
    mode: str = "simulated"
    seed: int | None = None
    total_laps: int = 58
    host: str = "127.0.0.1"
    port: int = 3001


@router.post("/start")
async def start_torcs(
    payload: TorcsStartRequest | None = None,
    torcs_service: TorcsService = Depends(get_torcs_service),
):
    payload = payload or TorcsStartRequest()

    if torcs_service.running:
        return {"status": "already running", "mode": payload.mode}

    asyncio.create_task(
        torcs_service.start(
            mode=payload.mode,
            seed=payload.seed,
            total_laps=payload.total_laps,
            host=payload.host,
            port=payload.port,
        )
    )

    return {"status": "torcs started", "mode": payload.mode}


@router.post("/stop")
async def stop_torcs(
    torcs_service: TorcsService = Depends(get_torcs_service),
):
    torcs_service.stop()
    return {"status": "torcs stopped"}
