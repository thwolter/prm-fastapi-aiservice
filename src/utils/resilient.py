"""Resilient execution utilities for handling service failures gracefully.

This module provides utilities for making service calls more resilient,
combining circuit breaker pattern with fallback functionality.
"""

import logging
from functools import wraps
from typing import Callable, TypeVar, Optional, Coroutine, Any, Union

from src.utils.circuit_breaker import get_circuit_breaker
from src.utils.exceptions import ExternalServiceException

# Type variable for generic function return type
T = TypeVar("T")

# Configure logger
logger = logging.getLogger(__name__)


def with_resilient_execution(
    service_name: Union[str, Callable[..., str]],
    create_default_response: Optional[Callable[..., Coroutine[Any, Any, T]]] = None,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """Decorator that combines circuit breaker and fallback functionality.

    Args:
        service_name: Name of the service being called. Can be a string or a callable
            that returns a string when called with the same arguments as the decorated function.
        create_default_response: Optional function to create a default response
            when the circuit is open or the service fails

    Returns:
        Decorated function with circuit breaker and fallback protection
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]]
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get the service name - either directly or by calling the function
            svc_name = service_name(*args, **kwargs) if callable(service_name) else service_name

            circuit = get_circuit_breaker(svc_name)

            # If circuit is open, fail fast
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker for {svc_name} is open, failing fast")
                if create_default_response:
                    return await create_default_response(*args, **kwargs)
                raise ExternalServiceException(
                    detail=f"Service {svc_name} is currently unavailable", service_name=svc_name
                )

            try:
                result = await func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as error:  # pragma: no cover - unexpected error
                circuit.record_failure()
                logger.warning(f"Service {svc_name} failed: {error}")
                if create_default_response:
                    return await create_default_response(*args, **kwargs)
                raise ExternalServiceException(
                    detail=f"Service {svc_name} failed: {str(error)}",
                    service_name=svc_name,
                )

        return wrapper

    return decorator
