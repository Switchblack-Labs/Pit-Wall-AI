from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Pit Wall AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    GRANITE_API_KEY: str = ""
    GRANITE_MODEL: str = "ibm-granite/granite-3.3-8b-instruct"

    LLM_PROVIDER: str = "auto"
    LLM_FALLBACK_ORDER: str = "watsonx,replicate,ollama,echo"

    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL: str = "ibm/granite-3-3-8b-instruct"

    REPLICATE_API_TOKEN: str = ""
    REPLICATE_MODEL: str = "ibm-granite/granite-3.3-8b-instruct"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "granite3.3:8b"

    NVIDIA_NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_NIM_API_KEY: str = ""
    NVIDIA_NIM_MODEL: str = "meta/llama3-70b-instruct"

    MOCK_TELEMETRY_MODE: bool = True
    TELEMETRY_SOURCE: str = "mock"

    WS_HEARTBEAT_INTERVAL: int = 30

    LANGFLOW_URL: str = ""
    LANGFLOW_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
