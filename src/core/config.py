import json
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RiskGPTSettings(BaseSettings):
    """Settings for RiskGPT related configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="RISKGPT_", env_ignore_empty=True, extra="ignore"
    )

    OPENAI_API_KEY: str | None = None
    MODEL_NAME: str | None = None
    TEMPERATURE: float | None = None


def parse_cors(v: Any) -> list[str] | str:
    """Parse BACKEND_CORS_ORIGINS from env allowing comma separated strings."""
    if not v:
        return []

    if isinstance(v, str):
        if v == "*":
            return v
        if v.startswith("["):
            try:
                origins = json.loads(v)
            except ValueError as e:  # pragma: no cover - invalid env value
                raise ValueError(v) from e
        else:
            origins = v.split(",")
    elif isinstance(v, list):
        origins = v
    else:
        raise ValueError(v)

    cleaned = []
    for origin in origins:
        s = str(origin).strip().rstrip("/")
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_ignore_empty=True, extra="ignore")
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "production"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == "production"

    APP_PORT: int = 8001
    APP_HOST: str = "localhost"
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
    LANGCHAIN_PROJECT: str

    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TIMEOUT: int = 60 * 60 * 24

    SENTRY_DSN: str
    LOG_LEVEL: str = "ERROR"

    SECRET_KEY: str
    SERVICE_SECRET: str
    AUTH_TOKEN_LEEWAY: int = 0  # in seconds
    AUTH_TOKEN_ALGORITHM: str = "HS256"
    AUTH_TOKEN_AUDIENCE: str = "fastapi-users:auth"

    OPENMETER_API_KEY: str
    OPENMETER_API_URL: str = "https://openmeter.cloud"
    OPENMETER_SOURCE: str = "prm-ai-service"
    OPENMETER_TIMEOUT: float = 1.0
    OPENMETER_FEATURE_KEY: str = "ai_tokens"

    @classmethod
    def from_env(cls):
        return cls()


settings = Settings()


def build_riskgpt_settings(base: Settings) -> RiskGPTSettings:
    """Create ``RiskGPTSettings`` using ``base`` values as fallbacks."""
    env_cfg = RiskGPTSettings()
    return RiskGPTSettings(
        OPENAI_API_KEY=env_cfg.OPENAI_API_KEY or base.OPENAI_API_KEY,
        MODEL_NAME=env_cfg.MODEL_NAME or base.OPENAI_MODEL_NAME,
        TEMPERATURE=env_cfg.TEMPERATURE or base.OPENAI_TEMPERATURE,
    )


riskgpt_settings = build_riskgpt_settings(settings)
