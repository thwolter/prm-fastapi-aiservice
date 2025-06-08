import pytest

from src.core.config import settings


@pytest.fixture(scope='session', autouse=True)
def load_env():
    settings.from_env()
    assert settings.OPENAI_API_KEY, 'OPENAI_API_KEY is not set'
    assert settings.LANGCHAIN_API_KEY, 'LANGCHAIN_API_KEY is not set'


@pytest.fixture(autouse=True)
def override_settings(request):
    """Override settings for testing."""
    redis_url = getattr(request, 'param', 'redis://localhost:6379')
    original_redis_url = settings.REDIS_URL
    settings.REDIS_URL = redis_url
    yield
    settings.REDIS_URL = original_redis_url
