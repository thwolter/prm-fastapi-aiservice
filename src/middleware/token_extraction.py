from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.auth.auth import get_jwt_payload
from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenExtractionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract the token from the request and attach it to the request's state.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        logger.debug(f"Cookies received in middleware: {request.cookies}")

        # In local environment, set dummy token and user ID
        if settings.ENVIRONMENT == "local":
            logger.debug("Local environment: setting dummy token and user ID")
            request.state.token = "dummy_token"
            request.state.user_id = "00000000-0000-0000-0000-000000000000"
            response: Response = await call_next(request)
            return response

        token = request.cookies.get("auth")

        if not token:
            logger.debug("No 'auth' token found in cookies")

        if token:
            try:
                payload = get_jwt_payload(request)
                request.state.token = token
                request.state.user_id = payload.get("sub")
            except HTTPException:
                request.state.token = None
                request.state.user_id = None

        final_response: Response = await call_next(request)
        return final_response
