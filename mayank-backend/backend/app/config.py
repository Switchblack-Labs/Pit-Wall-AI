from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Pit Wall AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # --- Legacy Granite settings (kept for backward compatibility) ---
    GRANITE_API_KEY: str = ""
    GRANITE_MODEL: str = "ibm-granite/granite-3.3-8b-instruct"

    # --- LLM provider selection ---
    # Explicit provider: "watsonx" | "replicate" | "ollama" | "echo" | "auto".
    # "auto" (default) picks the first provider whose credentials are present,
    # falling back to the deterministic offline "echo" provider.
    LLM_PROVIDER: str = "auto"
    # Ordered preference used by the auto-selector and for runtime fallback.
    LLM_FALLBACK_ORDER: str = "watsonx,replicate,ollama,echo"

    # IBM watsonx.ai
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL: str = "ibm/granite-3-3-8b-instruct"

    # Replicate-hosted Granite
    REPLICATE_API_TOKEN: str = ""
    REPLICATE_MODEL: str = "ibm-granite/granite-3.3-8b-instruct"

    # Local Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "granite3.3:8b"

    # --- Telemetry / TORCS ---
    MOCK_TELEMETRY_MODE: bool = True
    TELEMETRY_SOURCE: str = "mock"

    WS_HEARTBEAT_INTERVAL: int = 30

    # --- LangFlow (optional orchestration server) ---
    # When set, orchestration calls a running LangFlow server; otherwise the
    # in-process Python pipelines are used (they remain the source of truth).
    LANGFLOW_URL: str = ""
    LANGFLOW_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()