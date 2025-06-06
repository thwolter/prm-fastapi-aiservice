# Authentication

The service uses JWT-based authentication. Clients obtain a token from the `/auth/login` endpoint of the data service. The token is stored as an HTTP-only cookie named `auth`.

## Workflow
1. The `login` route forwards credentials to the data service and sets the `auth` cookie.
2. The `TokenExtractionMiddleware` reads the cookie on each request, decodes it using the secret defined in `.env`, and stores the token and `user_id` on `request.state`.
3. Routes use the `get_current_user` dependency to ensure a valid token is present.
4. `AuthService` checks the user's token quota via the data service before executing queries and reports consumed tokens afterwards.

See `app/auth` for implementation details.
