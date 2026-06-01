import asyncio

from fastapi import APIRouter, Depends

from app.dependencies import get_demo_service
from app.services.demo_service import DemoService

router = APIRouter(
    prefix="/api/demo",
    tags=["demo"]
)


@router.post("/start")
async def start_demo(
    demo_service: DemoService = Depends(
        get_demo_service
    )
):

    asyncio.create_task(
        demo_service.start()
    )

    return {
        "status": "demo started"
    }


@router.post("/stop")
async def stop_demo(
    demo_service: DemoService = Depends(
        get_demo_service
    )
):

    demo_service.stop()

    return {
        "status": "demo stopped"
    }