import pytest

pytest_plugins = [
    "tests.fixtures.env",
    "tests.fixtures.auth",
    "tests.fixtures.client",
    "tests.fixtures.quota",
    "tests.fixtures.meter",
]


# todo: das klappt nicht
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Set environment to 'testing' for tests marked with integration."""
    from src.core import config

    if any(mark.name == "integration" for mark in item.iter_markers()):
        original_environment = config.settings.ENVIRONMENT
        config.settings.ENVIRONMENT = "testing"

        # Store original environment to restore it later
        item._original_environment = original_environment


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Restore original environment after integration tests."""
    from src.core import config

    if hasattr(item, "_original_environment"):
        config.settings.ENVIRONMENT = item._original_environment
