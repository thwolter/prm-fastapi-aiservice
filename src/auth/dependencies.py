import jwt
from fastapi import Header, Request

from src.core.config import settings
from src.utils.exceptions import AuthenticationException


async def verify_service_jwt(
    request: Request,
    service_authorization: str | None = Header(None, alias='X-Service-Authorization'),
) -> None:
    """Validate service JWT from ``X-Service-Authorization`` header."""
    if settings.ENVIRONMENT == 'local':  # skip auth locally
        return

    if not service_authorization or not service_authorization.startswith('Bearer '):
        raise AuthenticationException(detail='Missing service token')

    token = service_authorization.split(' ', 1)[1]
    try:
        jwt.decode(
            token,
            settings.SERVICE_SECRET,
            algorithms=[settings.AUTH_TOKEN_ALGORITHM],
            options={'require': ['exp', 'iss']},
            issuer='projectrm-backend',
        )
        request.state.raw_token = token
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationException(detail='Token has expired') from exc
    except jwt.InvalidTokenError as exc:  # includes incorrect issuer
        raise AuthenticationException(detail='Invalid token') from exc
