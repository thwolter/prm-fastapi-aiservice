"""Resilient execution utilities for handling service failures gracefully.

This module provides utilities for making service calls more resilient,
combining circuit breaker pattern with fallback functionality.
"""
import logging
from functools import wraps
from typing import Callable, TypeVar, Any, Optional

from riskgpt.utils import with_fallback
from src.utils.circuit_breaker import get_circuit_breaker
from src.utils.exceptions import ExternalServiceException

# Type variable for generic function return type
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)

def with_resilient_execution(service_name, create_default_response: Optional[Callable] = None):
    """Decorator that combines circuit breaker and fallback functionality.

    Args:
        service_name: Name of the service being called. Can be a string or a callable
            that returns a string when called with the same arguments as the decorated function.
        create_default_response: Optional function to create a default response
            when the circuit is open or the service fails

    Returns:
        Decorated function with circuit breaker and fallback protection
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Get the service name - either directly or by calling the function
            svc_name = service_name(*args, **kwargs) if callable(service_name) else service_name

            circuit = get_circuit_breaker(svc_name)

            # If circuit is open, fail fast
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker for {svc_name} is open, failing fast")
                if create_default_response:
                    return create_default_response(*args, **kwargs)
                raise ExternalServiceException(
                    detail=f"Service {svc_name} is currently unavailable",
                    service_name=svc_name
                )

            async def fallback_function(error: Any, *fb_args, **fb_kwargs):
                # Record failure in circuit breaker
                circuit.record_failure()

                # Log the error
                logger.warning(f"Service {svc_name} failed: {error}")

                # Return a default response if provided, otherwise raise exception
                if create_default_response:
                    return create_default_response(*fb_args, **fb_kwargs)
                raise ExternalServiceException(
                    detail=f"Service {svc_name} failed: {str(error)}",
                    service_name=svc_name
                )

            try:
                # Use with_fallback to wrap the function
                result = await with_fallback(
                    function=lambda: func(*args, **kwargs),
                    fallback_function=fallback_function,
                    fallback_args=args,
                    fallback_kwargs=kwargs
                )

                # Record success in circuit breaker
                circuit.record_success()
                return result

            except Exception as e:
                # Record failure in circuit breaker
                circuit.record_failure()
                # Re-raise the exception
                raise

        return wrapper
    return decorator
