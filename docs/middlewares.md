# Middlewares

This service uses several middleware components to handle cross-cutting concerns such as authentication, authorization, token entitlement, and error formatting.

## MiddlewareSkipMixin

The `MiddlewareSkipMixin` is a base class that provides functionality to determine if middleware processing should be skipped for certain paths. It's used by other middleware components to avoid processing requests to paths like documentation routes, health checks, and static files.

```python
class MiddlewareSkipMixin:
    # Paths that should bypass middleware processing
    excluded_paths = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/_health",
    }
    
    # Regex patterns for paths that should bypass middleware processing
    excluded_patterns = [
        r"^/health-check.*",
        r"^/static/.*",
    ]
```

The mixin provides a `should_skip_middleware` method that checks if a given request path should bypass middleware processing.

## AuthorizationMiddleware

The `AuthorizationMiddleware` extracts a Bearer token from the request headers, validates it, and enriches the request state with authentication information.

```python
class AuthorizationMiddleware(MiddlewareSkipMixin, BaseHTTPMiddleware):
    # ...
```

This middleware:
1. Extracts the JWT token from the `Authorization` header
2. Validates the token using `get_jwt_payload`
3. Stores the user ID and email in `request.state`
4. Returns a 401 response if the token is missing or invalid

The expected header format is:

```http
Authorization: Bearer <token>
```

## TokenEntitlementMiddleware

The `TokenEntitlementMiddleware` checks if a user has access to requested features based on their token entitlement and consumes tokens after request processing.

```python
class TokenEntitlementMiddleware(MiddlewareSkipMixin, BaseHTTPMiddleware):
    # ...
```

This middleware:
1. Checks the user's token balance and access rights before allowing the request to proceed
2. Returns a 403 response if the user doesn't have sufficient tokens or access
3. Consumes tokens after successful request processing (status code < 400)
4. Requires that the route handler sets response information in the request state

## Custom Error Format Middleware

The `custom_error_format_middleware` catches `RequestValidationError` exceptions and formats them into a standardized JSON response.

```python
async def custom_error_format_middleware(request: Request, call_next):
    # ...
```

This middleware:
1. Catches validation errors that occur during request processing
2. Formats them into a consistent JSON response with a 422 status code
3. Includes detailed error information in the response

Example response:

```json
{
    "detail": "Validation failed",
    "errors": [
        {
            "loc": ["body", "field_name"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

## Middleware Order

The order in which middleware components are applied is important. In this service, the middleware components are applied in the following order:

1. CORS Middleware
2. Custom Error Format Middleware
3. Token Entitlement Middleware
4. Authorization Middleware

This ensures that authentication and authorization checks are performed before processing the request, and that errors are properly formatted in the response.