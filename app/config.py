from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_dotenv():
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.root:
        dotenv_path = current_dir / '.env'
        if dotenv_path.exists():
            return str(dotenv_path)
        current_dir = current_dir.parent
    raise FileNotFoundError(".env file not found")

DOTENV = find_dotenv()
load_dotenv(DOTENV)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding='utf-8', extra='ignore')

    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
    LANGCHAIN_PROJECT: str

    @classmethod
    def from_env(cls):
        return cls()

try:
    settings = Settings.from_env()
except Exception as e:
    print(f"Error loading settings: {e}")
    raise
