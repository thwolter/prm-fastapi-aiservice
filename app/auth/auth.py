import jwt
from fastapi import Request, HTTPException

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
AUDIENCE = "fastapi-users:auth"


def get_jwt_payload(request: Request):
    """
    Extract and verify JWT token from the cookie.
    """
    token = request.cookies.get("auth")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")