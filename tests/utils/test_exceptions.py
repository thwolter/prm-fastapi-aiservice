"""Tests for the custom exception classes."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.utils.exceptions import (
    BaseServiceException,
    ValidationException,
    RequestException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ExternalServiceException,
    RateLimitException,
    QuotaExceededException,
    InternalServerException,
)


def test_base_service_exception():
    """Test that BaseServiceException works correctly."""
    exception = BaseServiceException(
        status_code=400, detail="Test error", headers={"X-Test": "test"}, error_code="TEST_ERROR"
    )

    assert exception.status_code == 400
    assert exception.detail == "Test error"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "TEST_ERROR"


def test_validation_exception():
    """Test that ValidationException works correctly."""
    errors = [{"loc": ["field"], "msg": "error", "type": "value_error"}]
    exception = ValidationException(
        detail="Validation error", errors=errors, headers={"X-Test": "test"}
    )

    assert exception.status_code == 422
    assert exception.detail == "Validation error"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "VALIDATION_ERROR"
    assert exception.errors == errors


def test_request_exception():
    """Test that RequestException works correctly."""
    exception = RequestException(detail="Invalid request", headers={"X-Test": "test"})

    assert exception.status_code == 400
    assert exception.detail == "Invalid request"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "INVALID_REQUEST"


def test_authentication_exception():
    """Test that AuthenticationException works correctly."""
    exception = AuthenticationException(detail="Authentication failed", headers={"X-Test": "test"})

    assert exception.status_code == 401
    assert exception.detail == "Authentication failed"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "AUTHENTICATION_ERROR"


def test_authorization_exception():
    """Test that AuthorizationException works correctly."""
    exception = AuthorizationException(detail="Authorization failed", headers={"X-Test": "test"})

    assert exception.status_code == 403
    assert exception.detail == "Authorization failed"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "AUTHORIZATION_ERROR"


def test_resource_not_found_exception():
    """Test that ResourceNotFoundException works correctly."""
    exception = ResourceNotFoundException(detail="Resource not found", headers={"X-Test": "test"})

    assert exception.status_code == 404
    assert exception.detail == "Resource not found"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "RESOURCE_NOT_FOUND"


def test_external_service_exception():
    """Test that ExternalServiceException works correctly."""
    exception = ExternalServiceException(
        detail="External service error", service_name="TestService", headers={"X-Test": "test"}
    )

    assert exception.status_code == 502
    assert exception.detail == "External service error"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "EXTERNAL_SERVICE_ERROR"
    assert exception.service_name == "TestService"


def test_rate_limit_exception():
    """Test that RateLimitException works correctly."""
    exception = RateLimitException(
        detail="Rate limit exceeded", retry_after=60, headers={"X-Test": "test"}
    )

    assert exception.status_code == 429
    assert exception.detail == "Rate limit exceeded"
    assert exception.headers == {"X-Test": "test", "Retry-After": "60"}
    assert exception.error_code == "RATE_LIMIT_EXCEEDED"
    assert exception.retry_after == 60


def test_quota_exceeded_exception():
    """Test that QuotaExceededException works correctly."""
    exception = QuotaExceededException(detail="Quota exceeded", headers={"X-Test": "test"})

    assert exception.status_code == 402
    assert exception.detail == "Quota exceeded"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "QUOTA_EXCEEDED"


def test_internal_server_exception():
    """Test that InternalServerException works correctly."""
    exception = InternalServerException(detail="Internal server error", headers={"X-Test": "test"})

    assert exception.status_code == 500
    assert exception.detail == "Internal server error"
    assert exception.headers == {"X-Test": "test"}
    assert exception.error_code == "INTERNAL_SERVER_ERROR"


def test_exception_handling_in_fastapi():
    """Test that the exceptions are handled correctly by FastAPI."""
    app = FastAPI()

    @app.get("/validation-error")
    def validation_error():
        raise ValidationException(detail="Validation error")

    @app.get("/request-error")
    def request_error():
        raise RequestException(detail="Invalid request")

    @app.get("/authentication-error")
    def authentication_error():
        raise AuthenticationException(detail="Authentication failed")

    @app.get("/authorization-error")
    def authorization_error():
        raise AuthorizationException(detail="Authorization failed")

    @app.get("/resource-not-found")
    def resource_not_found():
        raise ResourceNotFoundException(detail="Resource not found")

    @app.get("/external-service-error")
    def external_service_error():
        raise ExternalServiceException(detail="External service error", service_name="TestService")

    @app.get("/rate-limit-exceeded")
    def rate_limit_exceeded():
        raise RateLimitException(detail="Rate limit exceeded", retry_after=60)

    @app.get("/quota-exceeded")
    def quota_exceeded():
        raise QuotaExceededException(detail="Quota exceeded")

    @app.get("/internal-server-error")
    def internal_server_error():
        raise InternalServerException(detail="Internal server error")

    client = TestClient(app)

    # Test validation error
    response = client.get("/validation-error")
    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"

    # Test request error
    response = client.get("/request-error")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"

    # Test authentication error
    response = client.get("/authentication-error")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication failed"

    # Test authorization error
    response = client.get("/authorization-error")
    assert response.status_code == 403
    assert response.json()["detail"] == "Authorization failed"

    # Test resource not found
    response = client.get("/resource-not-found")
    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"

    # Test external service error
    response = client.get("/external-service-error")
    assert response.status_code == 502
    assert response.json()["detail"] == "External service error"

    # Test rate limit exceeded
    response = client.get("/rate-limit-exceeded")
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"
    assert response.headers["retry-after"] == "60"

    # Test quota exceeded
    response = client.get("/quota-exceeded")
    assert response.status_code == 402
    assert response.json()["detail"] == "Quota exceeded"

    # Test internal server error
    response = client.get("/internal-server-error")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
