import importlib

import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Ensure that the application's config is reloaded and required environment variables are set before any tests run.
    This is useful when environment variables may change between test runs or when using tools like pytest-dotenv.
    """
    from src.core import config

    old_settings = config.settings
    importlib.reload(config)
    # keep original settings instance to avoid breaking references
    old_settings.__dict__.update(config.settings.__dict__)
    config.settings = old_settings
    assert config.settings.OPENAI_API_KEY, "OPENAI_API_KEY is not set"
    assert config.settings.LANGCHAIN_API_KEY, "LANGCHAIN_API_KEY is not set"


@pytest.fixture(autouse=True)
def override_settings(request):
    """
    Temporarily override config settings (e.g., REDIS_URL and ENVIRONMENT) for each test.
    This allows tests to run with different settings without affecting the global config or other tests.
    Useful for isolating test environments and simulating different configurations.
    """
    from src.core import config

    redis_url = getattr(request, "param", "redis://localhost:6379")
    original_redis_url = config.settings.REDIS_URL
    original_environment = config.settings.ENVIRONMENT
    config.settings.REDIS_URL = redis_url
    config.settings.ENVIRONMENT = "local"
    yield
    config.settings.REDIS_URL = original_redis_url
    config.settings.ENVIRONMENT = original_environment
