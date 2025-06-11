from fastapi import Header, Request
import jwt

from src.core.config import settings
from src.utils.exceptions import AuthenticationException


async def get_current_user(request: Request):
    """
    Dependency to enforce token validation and access control.
    """
    token = getattr(request.state, "token", None)
    user_id = getattr(request.state, "user_id", None)

    if not token or not user_id:
        raise AuthenticationException(detail="Unauthorized")

    return {"token": token, "user_id": user_id}


async def verify_service_jwt(authorization: str | None = Header(None)) -> None:
    """Validate service JWT from Authorization header."""
    if settings.ENVIRONMENT == "local":  # skip auth locally
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException(detail="Missing service token")

    token = authorization.split(" ", 1)[1]
    try:
        jwt.decode(
            token,
            settings.SERVICE_SECRET,
            algorithms=[settings.AUTH_TOKEN_ALGORITHM],
            options={"require": ["exp", "iss"]},
            issuer="projectrm-backend",
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationException(detail="Token has expired") from exc
    except jwt.InvalidTokenError as exc:  # includes incorrect issuer
        raise AuthenticationException(detail="Invalid token") from exc
