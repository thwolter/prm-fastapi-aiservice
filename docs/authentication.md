# Authentication

This service uses JSON Web Tokens (JWT) supplied in the `Authorization` header to authenticate requests.
The `TokenExtractionMiddleware` reads the header, decodes the token with `get_jwt_payload` and stores
both the raw token and the user identifier on `request.state`.

Authentication is bypassed when `ENVIRONMENT` is set to `local`. In this case dummy
values are stored so that the rest of the application can operate without valid credentials.

The expected header format is:

```http
Authorization: Bearer <token>
```

If the header is missing or malformed, an `AuthenticationException` is raised and the
request will receive a `401` response.
