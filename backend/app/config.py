from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Pit Wall AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    GRANITE_API_KEY: str = ""
    GRANITE_MODEL: str = "granite"

    MOCK_TELEMETRY_MODE: bool = True
    TELEMETRY_SOURCE: str = "mock"

    WS_HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()