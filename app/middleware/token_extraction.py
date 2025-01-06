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
        logger.info('Extracting token from request...')

        token = request.cookies.get('auth')
        logger.info(f'Extracted token: {token}')
        logger.info(f'Extracted cookies: {request.cookies}')

        request.state.token = token  # Attach token to request state
        request.state.user_id = None
        if token:
            try:
                payload = get_jwt_payload(request)
                # todo: check for token expiration with payload.get('exp')
                request.state.user_id = payload.get('sub')
            except Exception:
                logger.error('Token expired or invalid')

        return await call_next(request)
