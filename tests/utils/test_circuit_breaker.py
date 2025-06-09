"""Tests for the circuit breaker pattern implementation."""
import time
import pytest
from unittest.mock import patch, MagicMock

from src.utils.circuit_breaker import CircuitBreaker, CircuitState, with_circuit_breaker
from src.utils.exceptions import ExternalServiceException

def test_circuit_breaker_initial_state():
    """Test that a new circuit breaker starts in the CLOSED state."""
    cb = CircuitBreaker(name="test")
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0
    assert cb.allow_request() is True

def test_circuit_breaker_opens_after_failures():
    """Test that the circuit breaker opens after reaching the failure threshold."""
    cb = CircuitBreaker(name="test", failure_threshold=3)
    
    # Record failures up to threshold
    for _ in range(3):
        cb.record_failure()
    
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3
    assert cb.allow_request() is False

def test_circuit_breaker_half_open_after_timeout():
    """Test that the circuit breaker transitions to half-open after timeout."""
    cb = CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=0.1)
    
    # Open the circuit
    for _ in range(3):
        cb.record_failure()
    
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False
    
    # Wait for timeout
    time.sleep(0.2)
    
    # Should now be in half-open state and allow one request
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN

def test_circuit_breaker_closes_after_success():
    """Test that the circuit breaker closes after a successful request in half-open state."""
    cb = CircuitBreaker(name="test", failure_threshold=3)
    
    # Open the circuit
    for _ in range(3):
        cb.record_failure()
    
    assert cb.state == CircuitState.OPEN
    
    # Manually set to half-open
    cb.state = CircuitState.HALF_OPEN
    
    # Record success
    cb.record_success()
    
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

def test_circuit_breaker_reopens_after_failure_in_half_open():
    """Test that the circuit breaker reopens after a failure in half-open state."""
    cb = CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=30, timeout_factor=2)
    
    # Open the circuit
    for _ in range(3):
        cb.record_failure()
    
    # Manually set to half-open
    cb.state = CircuitState.HALF_OPEN
    
    # Record failure
    cb.record_failure()
    
    assert cb.state == CircuitState.OPEN
    assert cb.current_timeout == 60  # 30 * 2

def test_with_circuit_breaker_decorator_success():
    """Test that the decorator allows successful calls."""
    mock_func = MagicMock(return_value="success")
    
    @with_circuit_breaker(service_name="test")
    def test_func():
        return mock_func()
    
    result = test_func()
    
    assert result == "success"
    mock_func.assert_called_once()

def test_with_circuit_breaker_decorator_failure():
    """Test that the decorator handles failures correctly."""
    mock_func = MagicMock(side_effect=Exception("test error"))
    
    @with_circuit_breaker(service_name="test_failure")
    def test_func():
        return mock_func()
    
    # First call should raise the original exception
    with pytest.raises(Exception, match="test error"):
        test_func()
    
    mock_func.assert_called_once()

def test_with_circuit_breaker_decorator_open_circuit():
    """Test that the decorator fails fast when the circuit is open."""
    # Create a circuit breaker and open it
    from src.utils.circuit_breaker import _circuit_breakers
    cb = CircuitBreaker(name="test_open", failure_threshold=1)
    _circuit_breakers["test_open"] = cb
    cb.record_failure()  # Open the circuit
    
    mock_func = MagicMock(return_value="success")
    
    @with_circuit_breaker(service_name="test_open")
    def test_func():
        return mock_func()
    
    # Should raise ExternalServiceException without calling the function
    with pytest.raises(ExternalServiceException, match="Service test_open is currently unavailable"):
        test_func()
    
    mock_func.assert_not_called()

def test_with_circuit_breaker_decorator_fallback():
    """Test that the decorator returns the fallback value when the circuit is open."""
    # Create a circuit breaker and open it
    from src.utils.circuit_breaker import _circuit_breakers
    cb = CircuitBreaker(name="test_fallback", failure_threshold=1)
    _circuit_breakers["test_fallback"] = cb
    cb.record_failure()  # Open the circuit
    
    mock_func = MagicMock(return_value="success")
    
    @with_circuit_breaker(service_name="test_fallback", fallback_value="fallback")
    def test_func():
        return mock_func()
    
    # Should return the fallback value without calling the function
    result = test_func()
    
    assert result == "fallback"
    mock_func.assert_not_called()