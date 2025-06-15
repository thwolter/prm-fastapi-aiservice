from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from middleware.middleware_mixins import MiddlewareSkipMixin
from src.auth.auth import get_jwt_payload
from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class AuthorizationMiddleware(MiddlewareSkipMixin, BaseHTTPMiddleware):
    """
    Middleware to extract the token from the request and attach it to the request's state.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Extract a Bearer token from the request headers, enrich `request.state`
        with authentication information, and return early with a clear 401
        message if the header is missing or the token is invalid.
        """

        # Check if we should skip middleware processing for this path
        if self.should_skip_middleware(request):
            return await call_next(request)

        if settings.ENVIRONMENT == "local":
            logger.debug("Local environment: injecting dummy credentials")
            request.state.user_id = None
            request.state.user_email = None
            return await call_next(request)

        try:
            payload = get_jwt_payload(request)
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        response: Response = await call_next(request)
        return response
