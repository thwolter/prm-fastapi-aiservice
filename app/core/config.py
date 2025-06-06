from pathlib import Path
from typing import Annotated, Any, Literal

from dotenv import load_dotenv
from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_dotenv():
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.root:
        dotenv_path = current_dir / '.env'
        if dotenv_path.exists():
            return str(dotenv_path)
        current_dir = current_dir.parent
    raise FileNotFoundError('.env file not found')


DOTENV = find_dotenv()
load_dotenv(DOTENV)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith('['):
        return [i.strip() for i in v.split(',')]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True, extra='ignore')
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal['local', 'staging', 'production'] = 'production'

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == 'production'

    APP_PORT: int = 8001
    APP_HOST: str = 'localhost'
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
    LANGCHAIN_PROJECT: str

    OPENAI_MODEL_NAME: str = 'gpt-4o-mini'
    OPENAI_TEMPERATURE: float = 0.7

    REDIS_URL: str = 'redis://localhost:6379/0'
    CACHE_TIMEOUT: int = 60 * 60 * 24

    DATASERVICE_URL: AnyUrl
    SENTRY_DSN: str
    LOG_LEVEL: str = 'ERROR'

    SECRET_KEY: str
    AUTH_TOKEN_LEEWAY: int = -30  # in seconds
    AUTH_TOKEN_ALGORITHM: str = 'HS256'
    AUTH_TOKEN_AUDIENCE: str = 'fastapi-users:auth'

    PROMPT_SOURCE: Literal['file', 'hub'] = 'file'
    PROMPT_DIR: str = 'prompts'

    @classmethod
    def from_env(cls):
        return cls()


settings = Settings()
