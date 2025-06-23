"""
Environment configuration fixtures for testing.

This file contains fixtures for setting up and managing the test environment.
"""

import importlib

import pytest


@pytest.fixture(scope='session', autouse=True)
def load_env():
    """
    Ensure that the application's config is reloaded and required environment variables are set.

    This fixture runs once per test session and ensures that all required environment
    variables are properly loaded before any tests run. It's useful when environment
    variables may change between test runs or when using tools like pytest-dotenv.

    Yields:
        None
    """
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
    """
    Temporarily override config settings for each test.

    This fixture allows tests to run with different settings without affecting
    the global config or other tests. It's useful for isolating test environments
    and simulating different configurations.

    Args:
        request: Pytest's request fixture for accessing test metadata.

    Yields:
        None
    """
    from src.core import config

    redis_url = getattr(request, 'param', 'redis://localhost:6379')
    original_redis_url = config.settings.REDIS_URL
    original_environment = config.settings.ENVIRONMENT
    config.settings.REDIS_URL = redis_url
    config.settings.ENVIRONMENT = 'local'
    yield
    config.settings.REDIS_URL = original_redis_url
    config.settings.ENVIRONMENT = original_environment


@pytest.fixture
def local_openmeter_environment():
    """
    Set environment specifically for openmeter tests.

    This fixture temporarily changes the environment setting to 'testing'
    for end-to-end tests, and restores the original setting afterward.

    Yields:
        None
    """
    from src.core import config

    original_openmeter_url = config.settings.OPENMETER_API_URL
    original_environment = config.settings.ENVIRONMENT

    config.settings.ENVIRONMENT = 'testing'  # or "staging"
    config.settings.OPENMETER_API_URL = config.settings.OPENMETER_LOCAL_API_URL

    yield

    config.settings.ENVIRONMENT = original_environment
    config.settings.OPENMETER_API_URL = original_openmeter_url
