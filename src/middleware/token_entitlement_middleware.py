# First, let's create a new middleware file: src/middleware/token_entitlement_middleware.py

from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.config import settings
from middleware.middleware_mixins import MiddlewareSkipMixin
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.utils import logutils
from src.utils.exceptions import QuotaExceededException

logger = logutils.get_logger(__name__)


class TokenEntitlementMiddleware(MiddlewareSkipMixin, BaseHTTPMiddleware):
    """
    Middleware to check entitlement access and consume tokens after request processing.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Check if the user has access to the requested feature and consume tokens after the request is processed.

        Args:
            request: The FastAPI request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            The response from the next middleware or route handler.

        Raises:
            QuotaExceededException: If the user doesn't have access to the requested feature.
        """

        # Check if we should skip middleware processing for this path
        if self.should_skip_middleware(request):
            return await call_next(request)

        # Check entitlement before processing the request
        entitlement_service = TokenQuotaServiceProvider.get_entitlement_service(request)
        try:
            has_access = await entitlement_service.has_access(
                feature_key=settings.OPENMETER_FEATURE_KEY
            )
        except Exception as e:
            logger.error(f"Error checking entitlement for user {request.state.user_id}: {e}")
            raise QuotaExceededException(detail="Error checking entitlement")

        if not has_access:
            raise QuotaExceededException(detail="Token quota exceeded")

        # Process the request
        response = await call_next(request)

        # Consume tokens after the request is processed
        # Only consume tokens if the response was successful
        if response.status_code < 400:
            token_service = TokenQuotaServiceProvider.get_token_consumption_service(request)

            # The response object should be available in the request state
            # This assumes that the route handler sets the result in the request state
            if hasattr(request.state, "result"):
                await token_service.consume_tokens()
            else:
                logger.warning("No result found in request state to consume tokens")

        return response
