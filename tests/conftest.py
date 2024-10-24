import pytest

from app.config import settings


@pytest.fixture(scope='session', autouse=True)
def load_env():
    settings.from_env()
    assert settings.OPENAI_API_KEY, 'OPENAI_API_KEY is not set'
    assert settings.LANGCHAIN_API_KEY, 'LANGCHAIN_API_KEY is not set'
