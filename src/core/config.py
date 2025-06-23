import json
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from riskgpt.config.settings import RiskGPTSettings as BaseRiskGPTSettings


class RiskGPTSettings(BaseRiskGPTSettings):
    """Settings for RiskGPT related configuration."""

    model_config = SettingsConfigDict(
        env_file=['.env', '../.env'], env_prefix='RISKGPT_', env_ignore_empty=True, extra='ignore'
    )


def parse_cors(v: Any) -> list[str] | str:
    """Parse BACKEND_CORS_ORIGINS from env allowing comma separated strings."""
    if not v:
        return []

    if isinstance(v, str):
        if v == '*':
            return v
        if v.startswith('['):
            try:
                origins = json.loads(v)
            except ValueError as e:  # pragma: no cover - invalid env value
                raise ValueError(v) from e
        else:
            origins = v.split(',')
    elif isinstance(v, list):
        origins = v
    else:
        raise ValueError(v)

    cleaned = []
    for origin in origins:
        s = str(origin).strip().rstrip('/')
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '../.env'], env_ignore_empty=True, extra='ignore'
    )
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal['local', 'debug', 'testing', 'staging', 'production'] = 'production'
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == 'production'

    APP_PORT: int = 8001
    APP_HOST: str = 'localhost'

    SENTRY_DSN: str = 'your-dsn-here'
    LOG_LEVEL: str = 'ERROR'

    SECRET_KEY: str = 'your-secret-key'
    SERVICE_SECRET: str = 'your-service-secret'

    # Authentication configuration
    AUTH_TOKEN_LEEWAY: int = 0  # in seconds
    AUTH_TOKEN_ALGORITHM: str = 'HS256'
    AUTH_TOKEN_AUDIENCE: str = 'fastapi-users:auth'

    # Vendor configuration
    METERING_VENDOR: str = 'openmeter'

    # OpenMeter configuration
    OPENMETER_API_KEY: str = 'your-apikey'
    OPENMETER_API_URL: str = 'https://openmeter.cloud'
    OPENMETER_LOCAL_API_URL: str = 'http://localhost:8888'
    OPENMETER_SOURCE: str = 'prm-ai-service'
    OPENMETER_TIMEOUT: float = 1.0
    OPENMETER_FEATURE_KEY: str = 'ai_tokens'
    OPENMETER_EVENT_TYPE: str = 'tokens'


settings = Settings()


riskgpt_settings = RiskGPTSettings()
