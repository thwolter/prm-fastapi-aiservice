import typing
from typing import Any

import jwt
from fastapi import Request

from src.core.config import settings
from src.utils.exceptions import AuthenticationException


def get_jwt_payload(request: Request) -> dict[str, Any]:
    """
    Extract and verify JWT token from the ``Authorization`` header.
    In local environment, authentication is bypassed.
    """
    # Skip authentication in local environment
    if settings.ENVIRONMENT == "local":
        # Return a dummy payload with a user ID
        return {"sub": "00000000-0000-0000-0000-000000000000"}

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationException(detail="Missing authentication token")

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.AUTH_TOKEN_ALGORITHM],
            audience=settings.AUTH_TOKEN_AUDIENCE,
            leeway=settings.AUTH_TOKEN_LEEWAY,
        )
        return typing.cast(dict[str, Any], payload)

    except jwt.ExpiredSignatureError:
        raise AuthenticationException(detail="Token has expired")

    except jwt.InvalidTokenError:
        raise AuthenticationException(detail="Invalid token")
