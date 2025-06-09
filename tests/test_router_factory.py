from unittest import mock

import pytest
from fastapi import APIRouter
from pydantic import BaseModel

from src.routes import create_router
from src.services.base_service import BaseService
from src.utils import logutils


# Configure logutils for tests
logutils.logging.basicConfig(level=logutils.logging.DEBUG)


class MockService(BaseService):
    """Mock service for testing."""

    chain_fn = mock.MagicMock()
    route_path = '/mock/service/'

    class QueryModel(BaseModel):
        query: str

    class ResultModel(BaseModel):
        result: str


class TestRouterFactory:
    """Tests for the router_factory module."""

    def test_create_router_normal(self):
        """Test that create_router creates a router with routes for all discovered services."""
        # Mock the service discovery function to return a list of mock services
        mock_discover_services = mock.MagicMock(return_value=[MockService])

        # Call the function
        router = create_router(service_discovery_fn=mock_discover_services)

        # Verify that the router is an APIRouter
        assert isinstance(router, APIRouter)

        # Verify that the router has the correct prefix
        assert router.prefix == '/api'

        # Verify that the router has the correct responses
        assert router.responses == {404: {'description': 'Not found'}}

        # Verify that the service discovery function was called
        mock_discover_services.assert_called_once()

        # Verify that the router has routes
        assert len(router.routes) > 0

    def test_create_router_custom_prefix(self):
        """Test that create_router creates a router with a custom prefix."""
        # Mock the service discovery function to return a list of mock services
        mock_discover_services = mock.MagicMock(return_value=[MockService])

        # Call the function with a custom prefix
        router = create_router(
            prefix='/custom',
            service_discovery_fn=mock_discover_services
        )

        # Verify that the router has the correct prefix
        assert router.prefix == '/custom'

    def test_create_router_custom_responses(self):
        """Test that create_router creates a router with custom responses."""
        # Mock the service discovery function to return a list of mock services
        mock_discover_services = mock.MagicMock(return_value=[MockService])

        # Call the function with custom responses
        custom_responses = {404: {'description': 'Custom not found'}}
        router = create_router(
            responses=custom_responses,
            service_discovery_fn=mock_discover_services
        )

        # Verify that the router has the correct responses
        assert router.responses == custom_responses

    def test_create_router_no_services(self):
        """Test that create_router handles the case where no services are discovered."""
        # Mock the service discovery function to return an empty list
        mock_discover_services = mock.MagicMock(return_value=[])

        # Call the function
        router = create_router(service_discovery_fn=mock_discover_services)

        # Verify that the router is an APIRouter
        assert isinstance(router, APIRouter)

        # Verify that the service discovery function was called
        mock_discover_services.assert_called_once()

        # Verify that the router has no routes
        assert len(router.routes) == 0

    def test_create_router_service_discovery_error(self):
        """Test that create_router handles errors in service discovery."""
        # Mock the service discovery function to raise an exception
        mock_discover_services = mock.MagicMock(side_effect=Exception("Test exception"))

        # Call the function - it should not raise an exception
        router = create_router(service_discovery_fn=mock_discover_services)

        # Verify that the router is an APIRouter
        assert isinstance(router, APIRouter)

        # Verify that the service discovery function was called
        mock_discover_services.assert_called_once()

        # Verify that the router has no routes
        assert len(router.routes) == 0

    def test_create_router_route_registration_error(self):
        """Test that create_router handles errors in route registration."""
        # Create a mock service class that will cause an error during route registration
        class ErrorService(BaseService):
            route_path = '/error/service/'
            # Missing required attributes

        # Mock the service discovery function to return the error service
        mock_discover_services = mock.MagicMock(return_value=[ErrorService])

        # Call the function - it should not raise an exception
        router = create_router(service_discovery_fn=mock_discover_services)

        # Verify that the router is an APIRouter
        assert isinstance(router, APIRouter)

        # Verify that the service discovery function was called
        mock_discover_services.assert_called_once()

        # Verify that the router has no routes (since registration failed)
        assert len(router.routes) == 0


if __name__ == "__main__":
    pytest.main(["-v", "test_router_factory.py"])
