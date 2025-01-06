import logging

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.auth import get_jwt_payload

logger = logging.getLogger(__name__)


class TokenExtractionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract the token from the request and attach it to the request's state.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        logger.debug(f'Cookies received in middleware: {request.cookies}')
        token = request.cookies.get('auth')

        if not token:
            logger.debug("No 'auth' token found in cookies")

        if token:
            try:
                payload = get_jwt_payload(request)
                request.state.token = token
                request.state.user_id = payload.get('sub')
            except HTTPException:
                request.state.token = None
                request.state.user_id = None

        return await call_next(request)
