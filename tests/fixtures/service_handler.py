from typing import Any, Callable, Optional
from unittest import mock

import pytest

from src.routes.service_handler import ServiceHandler


@pytest.fixture
def mock_service_handler_handle():
    """
    Fixture that provides a mock for ServiceHandler.handle method.

    Returns:
        A mock object that can be configured with return_value or side_effect.
    """
    with mock.patch.object(ServiceHandler, "handle") as mock_handle:
        yield mock_handle


@pytest.fixture
def service_handler_with_mock_handle(mock_service_handler_handle):
    """
    Fixture that provides a ServiceHandler instance with a mocked handle method.

    Args:
        mock_service_handler_handle: The mocked handle method.

    Returns:
        A tuple containing (ServiceHandler instance, mock_handle).
    """
    # Create a minimal ServiceHandler instance
    handler = ServiceHandler(
        service_factory=lambda: None,  # Dummy factory
        request_model=None,  # Will be overridden by the mock
        response_model=None,  # Will be overridden by the mock
    )

    return handler, mock_service_handler_handle


@pytest.fixture
def configure_mock_handle(mock_service_handler_handle):
    """
    Fixture that provides a function to configure the mocked handle method.

    Args:
        mock_service_handler_handle: The mocked handle method.

    Returns:
        A function that can be used to configure the mock with a return value or side effect.
    """

    def _configure(return_value: Any = None, side_effect: Optional[Callable] = None):
        if side_effect is not None:
            mock_service_handler_handle.side_effect = side_effect
        else:
            mock_service_handler_handle.return_value = return_value
        return mock_service_handler_handle

    return _configure
