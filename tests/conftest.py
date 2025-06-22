"""
Global test configuration and fixtures.

This file configures pytest and imports all fixture modules to make them available to all tests.
"""

import pytest

pytest_plugins = [
    'tests.fixtures.environment',  # Renamed from env.py for clarity
    'tests.fixtures.auth',
    'tests.fixtures.test_clients',  # Renamed from client.py for clarity
    'tests.fixtures.service_handler',
    'tests.fixtures.local_openmeter',
]


# todo: das klappt nicht
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Set environment to 'testing' for tests marked with integration."""
    from src.core import config

    if any(mark.name == 'integration' for mark in item.iter_markers()):
        original_environment = config.settings.ENVIRONMENT
        config.settings.ENVIRONMENT = 'testing'

        # Store original environment to restore it later
        item._original_environment = original_environment


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Restore original environment after integration tests."""
    from src.core import config

    if hasattr(item, '_original_environment'):
        config.settings.ENVIRONMENT = item._original_environment
