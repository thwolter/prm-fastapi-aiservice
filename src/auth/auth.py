import jwt
from fastapi import HTTPException, Request

from src.core.config import settings


def get_jwt_payload(request: Request):
    """
    Extract and verify JWT token from the cookie.
    """
    token = request.cookies.get('auth')
    if not token:
        raise HTTPException(status_code=401, detail='Missing authentication token')

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
        raise HTTPException(status_code=401, detail='Token has expired')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')
