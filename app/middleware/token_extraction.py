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
        logger.debug(f"Cookies received in middleware: {request.cookies}")
        token = request.cookies.get('auth')

        if not token:
            logger.warning("No 'auth' token found in cookies")

        request.state.token = token  # Attach token to request state
        request.state.user_id = None

        if token:
            try:
                payload = get_jwt_payload(request)
                request.state.user_id = payload.get('sub')
            except Exception as e:
                logger.error(f"Error extracting token: {e}")

        return await call_next(request)
