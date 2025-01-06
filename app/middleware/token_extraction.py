import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.auth import get_jwt_payload

logger = logging.getLogger(__name__)


class TokenExtractionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract the token from the request and attach it to the request's state.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.cookies.get('auth')
        request.state.token = token  # Attach token to request state
        if token:
            try:
                payload = get_jwt_payload(request)
                request.state.user_id = payload.get('sub')
            except Exception:
                logger.error('Failed to extract user_id from token')
                request.state.user_id = None
        else:
            request.state.user_id = None

        return await call_next(request)
