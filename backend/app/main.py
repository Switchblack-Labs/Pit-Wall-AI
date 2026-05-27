from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.health import router as health_router
from app.utils.logger import logger

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