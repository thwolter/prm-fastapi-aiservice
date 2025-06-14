import jwt
from fastapi import Header, Request

from src.core.config import settings
from src.utils.exceptions import AuthenticationException


# todo: seem only be used in tests, consider removing
async def get_current_user(request: Request) -> dict[str, str]:
    """
    Dependency to enforce token validation and access control.
    In local environment, authentication is bypassed.
    """
    # Skip authentication in local environment
    if settings.ENVIRONMENT == "local":
        # Return a dummy user with a dummy token and user ID
        return {"token": "dummy_token", "user_id": "00000000-0000-0000-0000-000000000000"}

    token = getattr(request.state, "token", None)
    user_id = getattr(request.state, "user_id", None)

    if not token or not user_id:
        raise AuthenticationException(detail="Unauthorized")

    return {"token": token, "user_id": user_id}


async def verify_service_jwt(
    request: Request,
    service_authorization: str | None = Header(None, alias="X-Service-Authorization"),
) -> None:
    """Validate service JWT from ``X-Service-Authorization`` header."""
    if settings.ENVIRONMENT == "local":  # skip auth locally
        return

    if not service_authorization or not service_authorization.startswith("Bearer "):
        raise AuthenticationException(detail="Missing service token")

    token = service_authorization.split(" ", 1)[1]
    try:
        jwt.decode(
            token,
            settings.SERVICE_SECRET,
            algorithms=[settings.AUTH_TOKEN_ALGORITHM],
            options={"require": ["exp", "iss"]},
            issuer="projectrm-backend",
        )
        request.state.raw_token = token
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationException(detail="Token has expired") from exc
    except jwt.InvalidTokenError as exc:  # includes incorrect issuer
        raise AuthenticationException(detail="Invalid token") from exc
