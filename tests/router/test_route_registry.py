"""Tests for the route_registry module."""
import pytest
from unittest import mock
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
        service_factory = lambda: TestService()

        # Register a route
        registry.register_route(
            path="/test",
            request_model=TestRequestModel,
            response_model=TestResponseModel,
            service_factory=service_factory,
            tags=["test"]
        )

        # Check that router.post was called with the correct arguments
        router.post.assert_called_once_with(
            "/test",
            response_model=TestResponseModel,
            tags=["test"]
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

        # Create a route registry
        registry = RouteRegistry(router)

        # Create a service factory
        service_factory = lambda: TestService()

        # Register a route
        registry.register_route(
            path="/test",
            request_model=TestRequestModel,
            response_model=TestResponseModel,
            service_factory=service_factory,
            tags=["test"]
        )

        # Check that the route function was captured
        assert route_function is not None

        # Create a mock request
        request = mock.MagicMock(spec=Request)

        # Create a mock auth dependency
        async def mock_auth_dependency(request):
            return {"user_id": "test_user"}

        # Create a mock token service
        with mock.patch("src.router.routes.route_registry.TokenService") as MockTokenService:
            # Configure the mock token service
            mock_token_service = MockTokenService.return_value
            mock_token_service.has_access.return_value = True

            # Call the route function
            result = await route_function(
                request=request,
                request_model=TestRequestModel(query="test"),
                user_info=await mock_auth_dependency(request)
            )

            # Check that the result is correct
            assert isinstance(result, TestResponseModel)
            assert result.result == "Result for test"

            # Check that token service methods were called
            MockTokenService.assert_called_once_with(request)
            mock_token_service.has_access.assert_called_once()
            mock_token_service.consume_tokens.assert_called_once()

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

        # Create a route registry
        registry = RouteRegistry(router)

        # Create a service factory
        service_factory = lambda: TestService()

        # Register a route
        registry.register_route(
            path="/test",
            request_model=TestRequestModel,
            response_model=TestResponseModel,
            service_factory=service_factory,
            tags=["test"]
        )

        # Check that the route function was captured
        assert route_function is not None

        # Create a mock request
        request = mock.MagicMock(spec=Request)

        # Create a mock auth dependency
        async def mock_auth_dependency(request):
            return {"user_id": "test_user"}

        # Create a mock token service
        with mock.patch("src.router.routes.route_registry.TokenService") as MockTokenService:
            # Configure the mock token service to indicate token quota exceeded
            mock_token_service = MockTokenService.return_value
            mock_token_service.has_access.return_value = False

            # Call the route function - should raise HTTPException
            with pytest.raises(HTTPException) as excinfo:
                await route_function(
                    request=request,
                    request_model=TestRequestModel(query="test"),
                    user_info=await mock_auth_dependency(request)
                )

            # Check that the exception has the correct status code and detail
            assert excinfo.value.status_code == 402
            assert "Token quota exceeded" in excinfo.value.detail

            # Check that token service methods were called
            MockTokenService.assert_called_once_with(request)
            mock_token_service.has_access.assert_called_once()
            mock_token_service.consume_tokens.assert_not_called()

    def test_register_route_custom_auth(self):
        """Test that register_route accepts a custom auth dependency."""
        # Create a mock router
        router = mock.MagicMock(spec=APIRouter)

        # Create a route registry
        registry = RouteRegistry(router)

        # Create a service factory
        service_factory = lambda: TestService()

        # Create a custom auth dependency
        async def custom_auth(request):
            return {"user_id": "custom_user"}

        # Register a route with a custom auth dependency
        registry.register_route(
            path="/test",
            request_model=TestRequestModel,
            response_model=TestResponseModel,
            service_factory=service_factory,
            tags=["test"],
            auth_dependency=custom_auth
        )

        # Check that router.post was called with the correct arguments
        router.post.assert_called_once_with(
            "/test",
            response_model=TestResponseModel,
            tags=["test"]
        )

        # Check that the route function was registered
        assert router.post.return_value.called
