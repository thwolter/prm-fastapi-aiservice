"""
Environment configuration fixtures for testing.

This file contains fixtures for setting up and managing the test environment.
"""

import pytest


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

    original_environment = config.settings.ENVIRONMENT
    config.settings.ENVIRONMENT = 'local'
    yield
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
