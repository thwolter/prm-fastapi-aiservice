# Resilient Execution

This document explains the resilient execution functionality implemented in the AI Service project, which combines circuit breaker pattern with fallback functionality to make service calls more robust and fault-tolerant.

## Overview

The AI Service uses a resilient execution approach to handle failures in external service calls gracefully. This approach combines two key patterns:

1. **Circuit Breaker Pattern**: Prevents cascading failures by failing fast when a service is unavailable
2. **Fallback Functionality**: Provides alternative responses when a service call fails

This combined approach ensures that the application remains responsive even when external services are experiencing issues.

## Implementation

The resilient execution functionality is implemented in the
`src/utils/resilient.py` module, which relies on the `pybreaker`/`aiobreaker`
libraries to provide circuit breaker semantics. The
`with_resilient_execution` decorator exposes this functionality.

### The `with_resilient_execution` Decorator

The `with_resilient_execution` decorator combines circuit breaker and fallback functionality:

```python
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
    # Implementation details...
```

The decorator:

1. Checks if the circuit is open for the specified service
2. If the circuit is open, returns a default response or raises an exception
3. If the circuit is closed, attempts to execute the function
4. If the function succeeds, records a success in the circuit breaker
5. If the function fails, records a failure in the circuit breaker and returns a fallback response

### Integration with RiskGPT's `with_fallback`

The decorator uses RiskGPT's `with_fallback` functionality to handle failures:

```python
# Use with_fallback to wrap the function
result = await with_fallback(
    function=lambda: func(*args, **kwargs),
    fallback_function=fallback_function,
    fallback_args=args,
    fallback_kwargs=kwargs
)
```

This integration allows for a more robust fallback mechanism that can handle various types of failures.

## Usage in BaseService

The `BaseService` class uses the `with_resilient_execution` decorator to make service calls more resilient:

```python
class BaseService:
    """Base service calling RiskGPT chains."""

    # ... other attributes and methods ...

    async def execute_query(self, query: BaseModel):
        """Execute a query using the chain function with resilient execution."""
        if not self.chain_fn:
            raise RuntimeError('riskgpt is not installed')

        # Use the resilient execution decorator to handle fallbacks and circuit breaking
        return await self._execute_with_resilience(query)

    def _create_default_response(self, query: BaseModel):
        """Create a default response when the service is unavailable."""
        return self.ResultModel(
            success=False,
            error=f"Service {self.__class__.__name__} is temporarily unavailable"
        )

    @with_resilient_execution(
        service_name=lambda self, query: self.__class__.__name__,
        create_default_response=lambda self, query: self._create_default_response(query)
    )
    async def _execute_with_resilience(self, query: BaseModel):
        """Execute the query with resilient execution."""
        return await self.chain_fn(query)
```

This implementation ensures that all service calls made through the `BaseService.execute_query` method are protected by the resilient execution functionality.

## Benefits

The resilient execution functionality provides several benefits:

1. **Improved Fault Tolerance**: The application can continue to function even when external services are unavailable
2. **Reduced Cascading Failures**: The circuit breaker prevents cascading failures by failing fast when a service is unavailable
3. **Graceful Degradation**: The fallback functionality allows the application to provide alternative responses when a service call fails
4. **Automatic Recovery**: The circuit breaker automatically attempts to recover when a service becomes available again

## Example: Adding Custom Fallback Logic

You can customize the fallback logic for a specific service by overriding the `_create_default_response` method:

```python
class MyCustomService(BaseService):
    """Custom service with specialized fallback logic."""

    chain_fn = chains.async_my_custom_chain
    route_path = '/my/custom/endpoint/'
    QueryModel = MyCustomRequest
    ResultModel = MyCustomResponse

    def _create_default_response(self, query: BaseModel):
        """Create a custom default response when the service is unavailable."""
        # Implement custom fallback logic here
        return self.ResultModel(
            success=False,
            error="Custom fallback message",
            fallback_data={"some": "fallback data"}
        )
```

This allows you to provide more meaningful fallback responses for specific services.

## Conclusion

The resilient execution functionality in the AI Service project provides a robust mechanism for handling failures in external service calls. By combining the circuit breaker pattern with fallback functionality, the application can continue to function even when external services are experiencing issues.
