"""
Service handler fixtures for testing.

This file contains fixtures for mocking and configuring the ServiceHandler class,
which is used to handle service requests in the application.
"""

from typing import Any, Callable, Optional
from unittest import mock
from unittest.mock import MagicMock

import pytest

from src.routes.service_handler import ServiceHandler


@pytest.fixture
def mock_service_handler_handle():
    """
    Fixture that provides a mock for ServiceHandler.handle method.

    This fixture patches the handle method of the ServiceHandler class,
    allowing tests to control its behavior without executing the actual method.

    Returns:
        mock.MagicMock: A mock object that can be configured with return_value or side_effect.
    """
    with mock.patch.object(ServiceHandler, 'handle') as mock_handle:
        yield mock_handle


# Dummy model classes for testing
class DummyRequest:
    pass


class DummyResponse:
    pass


@pytest.fixture
def service_handler_with_mock_handle(mock_service_handler_handle):
    """
    Fixture that provides a ServiceHandler instance with a mocked handle method.

    This fixture creates a ServiceHandler instance with minimal configuration
    and returns it along with the mocked handle method, allowing tests to
    use a ServiceHandler without executing the actual handle method.

    Args:
        mock_service_handler_handle: The mocked handle method from mock_service_handler_handle fixture.

    Returns:
        tuple: A tuple containing (ServiceHandler instance, mock_handle).
    """
    mock_service: MagicMock = MagicMock()

    # Create a minimal ServiceHandler instance
    handler: ServiceHandler = ServiceHandler(
        service_factory=lambda: mock_service,  # Dummy factory
        request_model=DummyRequest,  # Will be overridden by the mock
        response_model=DummyResponse,  # Will be overridden by the mock
    )

    return handler, mock_service_handler_handle


@pytest.fixture
def configure_mock_handle(mock_service_handler_handle):
    """
    Fixture that provides a function to configure the mocked handle method.

    This fixture returns a function that can be used to easily configure
    the mocked handle method with a return value or side effect, making
    it easier to set up test scenarios.

    Args:
        mock_service_handler_handle: The mocked handle method from mock_service_handler_handle fixture.

    Returns:
        Callable: A function that can be used to configure the mock with a return value or side effect.
    """

    def _configure(return_value: Any = None, side_effect: Optional[Callable] = None):
        """
        Configure the mocked handle method with a return value or side effect.

        Args:
            return_value: The value to be returned by the mock.
            side_effect: A function or exception to be called/raised when the mock is called.

        Returns:
            mock.MagicMock: The configured mock object.
        """
        if side_effect is not None:
            mock_service_handler_handle.side_effect = side_effect
        else:
            mock_service_handler_handle.return_value = return_value
        return mock_service_handler_handle

    return _configure
