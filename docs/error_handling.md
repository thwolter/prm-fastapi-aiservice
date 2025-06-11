# Error Handling Strategy

This document describes the error handling strategy implemented in the AI Service.

## Overview

The AI Service uses a robust error handling strategy with custom exception classes for different error types. This approach provides several benefits:

1. **Consistent error responses**: All errors follow a standard format, making it easier for clients to handle them.
2. **Detailed error information**: Each exception includes specific details about the error, such as error codes and messages.
3. **Proper HTTP status codes**: Each exception maps to an appropriate HTTP status code.
4. **Centralized error handling**: All exceptions inherit from a base class, making it easy to add global error handling logic.

## Exception Hierarchy

The exception hierarchy is as follows:

- `BaseServiceException`: The base class for all service exceptions.
  - `ValidationException`: Raised when data validation fails.
  - `RequestException`: Raised when there's an issue with the request structure.
  - `AuthenticationException`: Raised when authentication fails.
  - `AuthorizationException`: Raised when authorization fails.
  - `ResourceNotFoundException`: Raised when a requested resource is not found.
  - `ExternalServiceException`: Raised when an external service call fails.
  - `RateLimitException`: Raised when rate limits are exceeded.
  - `QuotaExceededException`: Raised when a user's quota is exceeded.
  - `InternalServerException`: Raised for unexpected internal server errors.

## Usage

To use these exceptions in your code, import them from `src.utils.exceptions` and raise them when appropriate:

```python
from src.utils.exceptions import ResourceNotFoundException

def get_user(user_id):
    user = db.get_user(user_id)
    if not user:
        raise ResourceNotFoundException(detail=f"User {user_id} not found")
    return user
```

## Error Response Format

When an exception is raised, it will be caught by FastAPI and converted to an HTTP response with the appropriate status code and a JSON body containing the error details:

```json
{
  "detail": "User 123 not found"
}
```

Some exceptions include additional information, such as validation errors or retry-after headers.

## Testing

The exception classes are thoroughly tested in `tests/test_exceptions.py`. The tests verify that:

1. Each exception has the correct properties (status code, detail, headers, error code).
2. The exceptions are handled correctly by FastAPI.

## Circuit Breaker Pattern

The AI Service implements the circuit breaker pattern to handle external service outages gracefully. This pattern prevents cascading failures by failing fast when a service is unavailable.

### Overview

The circuit breaker pattern works like an electrical circuit breaker:

1. **Closed State**: In normal operation, the circuit is closed and requests flow through to the external service.
2. **Open State**: After a number of consecutive failures, the circuit opens and requests fail fast without attempting to call the external service.
3. **Half-Open State**: After a timeout period, the circuit enters a half-open state where a single request is allowed through to test if the service has recovered.

### Implementation

The circuit breaker is implemented using the `pybreaker` library (through
`aiobreaker` for async support). The helper module
`src/utils/circuit_breaker.py` exposes a registry of circuit breakers via
`get_circuit_breaker` and a `with_circuit_breaker` decorator for convenience.

### Usage

To use the circuit breaker in your code, import the decorator and apply it to functions that make external API calls:

```python
from src.utils.circuit_breaker import with_circuit_breaker

@with_circuit_breaker(service_name='ExternalService')
def call_external_service():
    # Make the external API call
    response = requests.get('https://api.external-service.com/endpoint')
    return response.json()
```

The circuit breaker will:

1. Track failures and successes of the external service calls.
2. Open the circuit after a threshold of consecutive failures (default: 5).
3. Prevent further calls to the service when the circuit is open.
4. Automatically test the service after a timeout period (default: 30 seconds).
5. Close the circuit again when the service recovers.

### Configuration

The circuit breaker exposes several configuration options when created:

- `fail_max`: Number of consecutive failures before opening the circuit (default: 5)
- `timeout_duration`: How long the circuit stays open before allowing a test call (default: 60s)

### Benefits

Using the circuit breaker pattern provides several benefits:

1. **Prevents Cascading Failures**: When an external service is down, the circuit breaker prevents the failure from cascading to other parts of the system.
2. **Improves User Experience**: Users get immediate feedback instead of waiting for timeouts.
3. **Reduces Load on External Services**: When a service is struggling, the circuit breaker reduces the load on it, giving it time to recover.
4. **Automatic Recovery**: The circuit breaker automatically tests the service and resumes normal operation when it recovers.

## Future Improvements

Potential future improvements to the error handling strategy include:

1. Adding a middleware to catch and log all exceptions.
2. Implementing a more detailed error response format with additional fields.
3. Adding support for internationalization of error messages.
4. Enhancing the circuit breaker with metrics and monitoring capabilities.
