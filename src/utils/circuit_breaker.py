"""Circuit breaker pattern implementation for external API calls.

This module provides a circuit breaker implementation to handle external service outages gracefully.
The circuit breaker prevents cascading failures by failing fast when a service is unavailable.
"""
import time
import logging
from enum import Enum
from typing import Callable, TypeVar, Any, Dict, Optional
from functools import wraps

from src.utils.exceptions import ExternalServiceException

# Type variable for generic function return type
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Enum representing the possible states of a circuit breaker."""
    CLOSED = 'CLOSED'  # Normal operation, requests are allowed
    OPEN = 'OPEN'      # Circuit is open, requests fail fast
    HALF_OPEN = 'HALF_OPEN'  # Testing if service is back online

class CircuitBreaker:
    """Circuit breaker implementation for external API calls.
    
    This class implements the circuit breaker pattern to prevent cascading failures
    when external services are unavailable.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        timeout_factor: float = 2.0,
        max_timeout: int = 120
    ):
        """Initialize the circuit breaker.
        
        Args:
            name: Name of the service protected by this circuit breaker
            failure_threshold: Number of consecutive failures before opening the circuit
            recovery_timeout: Time in seconds to wait before trying to recover (half-open state)
            timeout_factor: Factor to multiply recovery_timeout by on consecutive failures
            max_timeout: Maximum recovery timeout in seconds
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout_factor = timeout_factor
        self.max_timeout = max_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.current_timeout = recovery_timeout
    
    def record_success(self) -> None:
        """Record a successful call and reset failure counters."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker for {self.name} closing after successful test request")
            self.state = CircuitState.CLOSED
            self.current_timeout = self.recovery_timeout  # Reset timeout
    
    def record_failure(self) -> None:
        """Record a failed call and update circuit state if needed."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker for {self.name} opening after {self.failure_count} consecutive failures")
            self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit breaker for {self.name} reopening after failed test request")
            self.state = CircuitState.OPEN
            # Increase timeout for next recovery attempt, up to max_timeout
            self.current_timeout = min(self.current_timeout * self.timeout_factor, self.max_timeout)
    
    def allow_request(self) -> bool:
        """Check if a request should be allowed based on the current circuit state."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time > self.current_timeout:
                logger.info(f"Circuit breaker for {self.name} entering half-open state after {self.current_timeout}s timeout")
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        
        # In HALF_OPEN state, allow one test request
        return True

# Dictionary to store circuit breakers by service name
_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create a circuit breaker for the specified service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        CircuitBreaker instance for the service
    """
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(name=service_name)
    return _circuit_breakers[service_name]

def with_circuit_breaker(service_name: str, fallback_value: Optional[Any] = None):
    """Decorator to apply circuit breaker pattern to a function.
    
    Args:
        service_name: Name of the service being called
        fallback_value: Optional value to return when circuit is open
        
    Returns:
        Decorated function with circuit breaker protection
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            circuit = get_circuit_breaker(service_name)
            
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker for {service_name} is open, failing fast")
                if fallback_value is not None:
                    return fallback_value
                raise ExternalServiceException(
                    detail=f"Service {service_name} is currently unavailable",
                    service_name=service_name
                )
            
            try:
                result = func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure()
                # Re-raise the original exception
                raise
        
        return wrapper
    
    return decorator