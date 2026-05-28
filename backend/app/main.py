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
from app.api.simulation import router as simulation_router
from app.api.explanation import router as explanation_router
from app.api.mock_data import router as mock_router
from app.api.demo import router as demo_router
from fastapi.exceptions import RequestValidationError
from app.api.rag import router as rag_router

from app.core.exceptions import (
    validation_exception_handler,
    generic_exception_handler
)


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
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
app.include_router(simulation_router)
app.include_router(explanation_router)
app.include_router(mock_router)
app.include_router(demo_router)
app.include_router(rag_router)

from app.api.rag import router as rag_router

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