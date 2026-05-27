from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.health import router as health_router
from app.api.telemetry import router as telemetry_router
from app.api.competitors import router as competitors_router
from app.api.websocket import router as websocket_router
from app.utils.logger import logger
from app.dependencies import get_race_state_service
from app.api.strategy import router as strategy_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(telemetry_router)
app.include_router(competitors_router)
app.include_router(websocket_router)
app.include_router(strategy_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Pit Wall backend starting")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Pit Wall backend shutting down")


@app.get("/")
def root():
    return {
        "status": "backend running",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/debug/state")
def debug_state():
    service = get_race_state_service()
    return service.get_state()