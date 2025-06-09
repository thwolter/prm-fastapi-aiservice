import jwt
from fastapi import Request

from src.core.config import settings
from src.utils.exceptions import AuthenticationException


def get_jwt_payload(request: Request):
    """
    Extract and verify JWT token from the cookie.
    """
    token = request.cookies.get('auth')
    if not token:
        raise AuthenticationException(detail='Missing authentication token')

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.AUTH_TOKEN_ALGORITHM],
            audience=settings.AUTH_TOKEN_AUDIENCE,
            leeway=settings.AUTH_TOKEN_LEEWAY,
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthenticationException(detail='Token has expired')

    except jwt.InvalidTokenError:
        raise AuthenticationException(detail='Invalid token')
