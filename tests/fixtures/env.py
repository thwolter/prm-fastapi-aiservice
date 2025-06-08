import importlib
import pytest


@pytest.fixture(scope='session', autouse=True)
def load_env():
    from src.core import config
    old_settings = config.settings
    importlib.reload(config)
    # keep original settings instance to avoid breaking references
    old_settings.__dict__.update(config.settings.__dict__)
    config.settings = old_settings
    assert config.settings.OPENAI_API_KEY, 'OPENAI_API_KEY is not set'
    assert config.settings.LANGCHAIN_API_KEY, 'LANGCHAIN_API_KEY is not set'


@pytest.fixture(autouse=True)
def override_settings(request):
    """Override settings for testing."""
    from src.core import config
    redis_url = getattr(request, 'param', 'redis://localhost:6379')
    original_redis_url = config.settings.REDIS_URL
    config.settings.REDIS_URL = redis_url
    yield
    config.settings.REDIS_URL = original_redis_url
