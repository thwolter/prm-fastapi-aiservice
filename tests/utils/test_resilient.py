"""Tests for the resilient execution utilities."""

import typing

import pytest
from unittest.mock import MagicMock, AsyncMock

from src.utils.resilient import with_resilient_execution
from src.utils.exceptions import ExternalServiceException


@pytest.mark.asyncio
async def test_with_resilient_execution_success():
    """Test that the decorator allows successful calls."""
    mock_func = AsyncMock(return_value="success")

    @with_resilient_execution(service_name="test")
    async def test_func():
        return await mock_func()

    result: str = await test_func()

    assert result == "success"
    mock_func.assert_called_once()


@pytest.mark.asyncio
async def test_with_resilient_execution_failure_with_fallback():
    """Test that the decorator handles failures with fallback."""
    mock_func = AsyncMock(side_effect=Exception("test error"))
    mock_fallback = MagicMock(return_value="fallback")

    @with_resilient_execution(service_name="test_fallback", create_default_response=mock_fallback)
    async def test_func():
        return await mock_func()

    result: str = await test_func()

    assert result == "fallback"
    mock_func.assert_called_once()
    mock_fallback.assert_called_once()


@pytest.mark.asyncio
async def test_with_resilient_execution_failure_with_async_fallback():
    """Fallback coroutine functions should also be awaited."""
    mock_func = AsyncMock(side_effect=Exception("test error"))
    mock_fallback = AsyncMock(return_value="fallback_async")

    @with_resilient_execution(
        service_name="test_async_fallback", create_default_response=mock_fallback
    )
    async def test_func():
        return await mock_func()

    result: str = await test_func()

    assert result == "fallback_async"
    mock_func.assert_called_once()
    mock_fallback.assert_awaited_once()


@pytest.mark.asyncio
async def test_with_resilient_execution_dynamic_service_name():
    """Test that the decorator handles dynamic service names."""
    mock_func = AsyncMock(return_value="success")

    @with_resilient_execution(service_name=lambda x: f"service_{x}")
    async def test_func(x):
        return await mock_func()

    result: str = await test_func(123)

    assert result == "success"
    mock_func.assert_called_once()


@pytest.mark.asyncio
async def test_with_resilient_execution_circuit_open():
    """Test that the decorator fails fast when the circuit is open."""
    # Create a circuit breaker and open it
    from src.utils.circuit_breaker import get_circuit_breaker

    cb = get_circuit_breaker("test_open")
    cb.open()

    mock_func = AsyncMock(return_value="success")

    @with_resilient_execution(service_name="test_open")
    async def test_func():
        return await mock_func()

    # Should raise ExternalServiceException without calling the function
    with pytest.raises(
        ExternalServiceException, match="Service test_open is currently unavailable"
    ):
        await test_func()

    mock_func.assert_not_called()


@pytest.mark.asyncio
async def test_with_resilient_execution_circuit_open_with_fallback():
    """Test that the decorator returns the fallback when the circuit is open."""
    # Create a circuit breaker and open it
    from src.utils.circuit_breaker import get_circuit_breaker

    cb = get_circuit_breaker("test_open_fallback")
    cb.open()

    mock_func = AsyncMock(return_value="success")
    mock_fallback = MagicMock(return_value="fallback")

    @with_resilient_execution(
        service_name="test_open_fallback", create_default_response=mock_fallback
    )
    async def test_func():
        return await mock_func()

    result = await test_func()

    assert result == "fallback"
    mock_func.assert_not_called()
    mock_fallback.assert_called_once()


@pytest.mark.asyncio
async def test_with_resilient_execution_error_no_fallback():
    """Ensure unexpected errors raise ExternalServiceException."""

    async def failing():
        raise RuntimeError("boom")

    wrapped: typing.Callable = with_resilient_execution(service_name="svc")(failing)

    with pytest.raises(ExternalServiceException, match="boom"):
        await wrapped()
