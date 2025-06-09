"""Tests for the service_handler module."""
import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from src.routes.service_handler import ServiceHandler


class TestRequestModel(BaseModel):
    """Test request model for service handler tests."""
    query: str


class TestResponseModel(BaseModel):
    """Test response model for service handler tests."""
    result: str
    response_info: dict = None


class TestService:
    """Test service for service handler tests."""

    async def execute_query(self, query):
        """Mock execute_query method."""
        return TestResponseModel(result=f"Result for {query.query}")


class TestServiceHandler:
    """Tests for the ServiceHandler class."""

    @pytest.mark.asyncio
    async def test_handle_valid_request(self):
        """Test that handle works with a valid request."""
        # Create a service factory
        service_factory = lambda: TestService()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request
        result = await handler.handle(request)

        # Check that the result is correct
        assert isinstance(result, TestResponseModel)
        assert result.result == "Result for test"

    @pytest.mark.asyncio
    async def test_handle_with_response_info(self):
        """Test that handle preserves response_info."""
        # Create a service with response_info
        class TestServiceWithResponseInfo:
            async def execute_query(self, query):
                return TestResponseModel(
                    result=f"Result for {query.query}",
                    response_info={"tokens": 100}
                )

        # Create a service factory
        service_factory = lambda: TestServiceWithResponseInfo()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request
        result = await handler.handle(request)

        # Check that the result is correct and has response_info
        assert isinstance(result, TestResponseModel)
        assert result.result == "Result for test"
        assert result.response_info == {"tokens": 100}

    @pytest.mark.asyncio
    async def test_handle_attribute_error(self):
        """Test that handle handles AttributeError correctly."""
        # Create a service that raises AttributeError
        class ErrorService:
            async def execute_query(self, query):
                raise AttributeError("Test attribute error")

        # Create a service factory
        service_factory = lambda: ErrorService()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request - should raise HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await handler.handle(request)

        # Check that the exception has the correct status code and detail
        assert excinfo.value.status_code == 400
        assert "Invalid request structure" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_handle_type_error(self):
        """Test that handle handles TypeError correctly."""
        # Create a service that raises TypeError
        class ErrorService:
            async def execute_query(self, query):
                raise TypeError("Test type error")

        # Create a service factory
        service_factory = lambda: ErrorService()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request - should raise HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await handler.handle(request)

        # Check that the exception has the correct status code and detail
        assert excinfo.value.status_code == 400
        assert "Invalid request structure" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_handle_http_exception(self):
        """Test that handle handles HTTPException correctly."""
        # Create a service that raises HTTPException
        class ErrorService:
            async def execute_query(self, query):
                raise HTTPException(status_code=403, detail="Test HTTP exception")

        # Create a service factory
        service_factory = lambda: ErrorService()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request - should raise HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await handler.handle(request)

        # Check that the exception has the correct status code and detail
        assert excinfo.value.status_code == 403
        assert "Test HTTP exception" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_handle_generic_exception(self):
        """Test that handle handles generic exceptions correctly."""
        # Create a service that raises a generic exception
        class ErrorService:
            async def execute_query(self, query):
                raise Exception("Test exception")

        # Create a service factory
        service_factory = lambda: ErrorService()

        # Create a service handler
        handler = ServiceHandler(service_factory, TestRequestModel, TestResponseModel)

        # Create a request
        request = TestRequestModel(query="test")

        # Handle the request - should raise HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await handler.handle(request)

        # Check that the exception has the correct status code and detail
        assert excinfo.value.status_code == 500
        assert "Internal Server Error" in excinfo.value.detail

    def test_get_service_name(self):
        """Test that _get_service_name works correctly."""
        # Create a named service factory
        def named_factory():
            return TestService()

        # Create a service handler
        handler = ServiceHandler(named_factory, TestRequestModel, TestResponseModel)

        # Check that _get_service_name returns the correct name
        assert handler._get_service_name() == "named_factory"

        # Create a lambda service factory
        lambda_factory = lambda: TestService()

        # Create a service handler
        handler = ServiceHandler(lambda_factory, TestRequestModel, TestResponseModel)

        # Check that _get_service_name returns a string representation
        assert isinstance(handler._get_service_name(), str)
