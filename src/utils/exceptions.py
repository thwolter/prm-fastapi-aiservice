"""Custom exception classes for the AI Service.

This module defines custom exception classes for different error types in the AI Service.
These exceptions are designed to be caught and handled appropriately by the service handlers
and middleware to provide consistent error responses to clients.
"""
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException


class BaseServiceException(HTTPException):
    """Base exception class for all service exceptions.
    
    All custom exceptions should inherit from this class to ensure consistent
    error handling and response formatting.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize the exception.
        
        Args:
            status_code: HTTP status code to return
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
            error_code: Optional error code for machine-readable error identification
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationException(BaseServiceException):
    """Exception raised when data validation fails."""
    
    def __init__(
        self,
        detail: str,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the validation exception.
        
        Args:
            detail: Human-readable error message
            errors: List of validation errors
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=422,
            detail=detail,
            headers=headers,
            error_code="VALIDATION_ERROR"
        )
        self.errors = errors


class RequestException(BaseServiceException):
    """Exception raised when there's an issue with the request structure."""
    
    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the request exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=400,
            detail=detail,
            headers=headers,
            error_code="INVALID_REQUEST"
        )


class AuthenticationException(BaseServiceException):
    """Exception raised when authentication fails."""
    
    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the authentication exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=401,
            detail=detail,
            headers=headers,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(BaseServiceException):
    """Exception raised when authorization fails."""
    
    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the authorization exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=403,
            detail=detail,
            headers=headers,
            error_code="AUTHORIZATION_ERROR"
        )


class ResourceNotFoundException(BaseServiceException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the resource not found exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=404,
            detail=detail,
            headers=headers,
            error_code="RESOURCE_NOT_FOUND"
        )


class ExternalServiceException(BaseServiceException):
    """Exception raised when an external service call fails."""
    
    def __init__(
        self,
        detail: str,
        service_name: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the external service exception.
        
        Args:
            detail: Human-readable error message
            service_name: Name of the external service that failed
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=502,
            detail=detail,
            headers=headers,
            error_code="EXTERNAL_SERVICE_ERROR"
        )
        self.service_name = service_name


class RateLimitException(BaseServiceException):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(
        self,
        detail: str,
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the rate limit exception.
        
        Args:
            detail: Human-readable error message
            retry_after: Seconds after which the client should retry
            headers: Optional HTTP headers to include in the response
        """
        headers = headers or {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=429,
            detail=detail,
            headers=headers,
            error_code="RATE_LIMIT_EXCEEDED"
        )
        self.retry_after = retry_after


class QuotaExceededException(BaseServiceException):
    """Exception raised when a user's quota is exceeded."""
    
    def __init__(
        self,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the quota exceeded exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=402,
            detail=detail,
            headers=headers,
            error_code="QUOTA_EXCEEDED"
        )


class InternalServerException(BaseServiceException):
    """Exception raised for unexpected internal server errors."""
    
    def __init__(
        self,
        detail: str = "Internal Server Error",
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the internal server exception.
        
        Args:
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(
            status_code=500,
            detail=detail,
            headers=headers,
            error_code="INTERNAL_SERVER_ERROR"
        )