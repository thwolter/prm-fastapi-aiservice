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
    ENVIRONMENT: Literal['local', 'staging', 'production'] = 'local'

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    APP_PORT: int = 8001
    APP_HOST: str = 'localhost'
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
    LANGCHAIN_PROJECT: str

    REDIS_URL: str = 'redis://localhost:6379/0'
    CACHE_TIMEOUT: int = 60 * 60 * 24

    SECRET_KEY: str
    DATASERVICE_URL: AnyUrl

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == 'local':
            return f'http://{self.DOMAIN}'
        return f'https://{self.DOMAIN}'

    @classmethod
    def from_env(cls):
        return cls()


settings = Settings()
