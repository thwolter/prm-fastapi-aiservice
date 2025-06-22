from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from src.api.dependencies import get_metering_service
from src.middleware.middleware_mixins import MiddlewareSkipMixin
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenMiddleware(MiddlewareSkipMixin, BaseHTTPMiddleware):
    """
    Middleware to check token entitlement and consume tokens after request processing.
    """

    def __init__(self, app):
        super().__init__(app)
        self.metering = get_metering_service()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Check if the user has sufficient tokens and consume tokens after request processing.

        Args:
            request: The FastAPI request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            The response from the next middleware or route handler.
        """
        # Check if we should skip middleware processing for this path
        if self.should_skip_middleware(request):
            return await call_next(request)

        # Check if user has a valid user_id in state
        if not hasattr(request.state, 'user_id'):
            logger.warning('User ID not found in request state')
            return JSONResponse(
                status_code=401,
                content={'detail': 'Authentication required'},
            )

        # Check token entitlement
        entitlement = await self.metering.check_entitlement(request.state.user_id)

        # Check if user has sufficient tokens
        if not entitlement['has_access']:
            return JSONResponse(
                status_code=403,
                content={
                    'detail': 'Insufficient token entitlement. Please check your subscription.'
                },
            )

        if entitlement['balance'] <= 0:
            return JSONResponse(
                status_code=403,
                content={
                    'detail': 'Insufficient token balance. Please add more tokens to your account.'
                },
            )

        # Process the request
        response = await call_next(request)

        # Consume tokens after the request is processed
        # Only consume tokens if the response was successful
        if response.status_code < 400:
            if hasattr(request.state, 'response_info'):
                await self.metering.consume_tokens(
                    subject_id=request.state.user_id,
                    tokens=request.state.response_info.consumed_tokens,
                    model=getattr(request.state.response_info, 'model_name', None),
                    prompt=getattr(request.state.response_info, 'prompt_name', None),
                )

        return response
