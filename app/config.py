import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

DOTENV = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(DOTENV)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_ignore_empty=True, extra="ignore")

    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
    LANGCHAIN_PROJECT: str


settings = Settings()