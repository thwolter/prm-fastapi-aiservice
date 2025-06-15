"""Tests for the route_registry module."""

from unittest import mock

import pytest
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.routes import RouteRegistry


class TestRequestModel(BaseModel):
    """Test request model for route registry tests."""

    query: str


class TestResponseModel(BaseModel):
    """Test response model for route registry tests."""

    result: str


class TestService:
    """Test service for route registry tests."""

    async def execute_query(self, query):
        """Mock execute_query method."""
        return TestResponseModel(result=f"Result for {query.query}")


class TestRouteRegistry:
    """Tests for the RouteRegistry class."""

    def test_init(self):
        """Test that RouteRegistry initializes correctly."""
        # Create a mock router
        router = mock.MagicMock(spec=APIRouter)

        # Create a route registry
        registry = RouteRegistry(router)

        # Check that the router is stored correctly
        assert registry.router == router

    def test_register_route(self):
        """Test that register_route registers a route correctly."""
        # Create a mock router
        router = mock.MagicMock(spec=APIRouter)

        # Create a route registry
        registry = RouteRegistry(router)

        # Create a service factory
        def service_factory():
            return TestService()

        # Register a route
        registry.register_route(
            path="/test",
            request_model=TestRequestModel,
            response_model=TestResponseModel,
            service_factory=service_factory,
            tags=["test"],
        )

        # Check that router.post was called with the correct arguments
        router.post.assert_called_once_with(
            "/test", response_model=TestResponseModel, tags=["test"]
        )

        # Check that the route function was registered
        assert router.post.return_value.called

    @pytest.mark.asyncio
    async def test_route_function(self):
        """Test that the route function works correctly."""
        # Create a mock router
        router = mock.MagicMock(spec=APIRouter)

        # Mock the post method to capture the route function
        route_function = None

        def post_side_effect(path, response_model, tags):
            def decorator(func):
                nonlocal route_function
                route_function = func
                return func

            return decorator

        router.post.side_effect = post_side_effect

        # Mock the environment to be 'local' to simplify testing
        with mock.patch("src.core.config.settings.ENVIRONMENT", "local"):
            # Create a route registry
            registry = RouteRegistry(router)

            # Create a service factory
            def service_factory():
                return TestService()

            # Register a route
            registry.register_route(
                path="/test",
                request_model=TestRequestModel,
                response_model=TestResponseModel,
                service_factory=service_factory,
                tags=["test"],
            )

            # Check that the route function was captured
            assert route_function is not None

            # Create a mock request
            request = mock.MagicMock(spec=Request)

            # Call the route function (in local environment, no auth/metering)
            # Mock the token
            token = "test_token"
            result = await route_function(
                request=request, token=token, request_model=TestRequestModel(query="test")
            )

            # Check that the result is correct
            assert isinstance(result, TestResponseModel)
            assert result.result == "Result for test"

    @pytest.mark.asyncio
    async def test_route_function_token_quota_exceeded(self):
        """Test that the route function handles token quota exceeded correctly."""
        # Create a mock router
        router = mock.MagicMock(spec=APIRouter)

        # Mock the post method to capture the route function
        route_function = None

        def post_side_effect(path, response_model, tags):
            def decorator(func):
                nonlocal route_function
                route_function = func
                return func

            return decorator

        router.post.side_effect = post_side_effect

        # Mock the environment to be 'local' to simplify testing
        with mock.patch("src.core.config.settings.ENVIRONMENT", "local"):
            # Create a route registry
            registry = RouteRegistry(router)

            # Create a service factory
            def service_factory():
                return TestService()

            # Register a route
            registry.register_route(
                path="/test",
                request_model=TestRequestModel,
                response_model=TestResponseModel,
                service_factory=service_factory,
                tags=["test"],
            )

            # Check that the route function was captured
            assert route_function is not None

            # Create a mock request
            request = mock.MagicMock(spec=Request)

            # Mock the ServiceHandler.handle method to raise QuotaExceededException
            with mock.patch("src.routes.service_handler.ServiceHandler.handle") as mock_handle:
                # Configure the mock to raise QuotaExceededException
                from src.utils.exceptions import QuotaExceededException

                mock_handle.side_effect = QuotaExceededException(detail="Token quota exceeded")

                # Call the route function - should raise HTTPException
                # Mock the token
                token = "test_token"
                with pytest.raises(HTTPException) as excinfo:
                    await route_function(
                        request=request, token=token, request_model=TestRequestModel(query="test")
                    )

                # Check that the exception has the correct status code and detail
                assert excinfo.value.status_code == 402
                assert "Token quota exceeded" in excinfo.value.detail
