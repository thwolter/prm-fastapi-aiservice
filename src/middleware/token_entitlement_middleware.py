from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from core.config import settings
from middleware.middleware_mixins import MiddlewareSkipMixin
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.utils import logutils
from src.utils.exceptions import QuotaExceededException, ResourceNotFoundException

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
            entitlement = await entitlement_service.get_entitlement_value(
                feature_key=settings.OPENMETER_FEATURE_KEY
            )
        except ResourceNotFoundException:
            logger.warning(f"Entitlement not found for user {request.state.user_id}")
            return JSONResponse(
                status_code=403,
                content={"detail": "User not found."},
            )
        except Exception as e:
            logger.error(f"Error checking entitlement for user {request.state.user_id}: {e}")
            raise QuotaExceededException(detail="Error checking entitlement")

        if entitlement["balance"] <= 0:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Insufficient token balance. Please add more tokens to your account."
                },
            )

        if not entitlement["hasAccess"]:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Insufficient token entitlement. Please check your subscription."
                },
            )

        # Process the request
        response = await call_next(request)

        # Consume tokens after the request is processed
        # Only consume tokens if the response was successful
        if response.status_code < 400:
            token_service = TokenQuotaServiceProvider.get_token_consumption_service(request)

            # The response object should be available in the request state
            # This assumes that the route handler sets the result in the request state
            if hasattr(request.state, "response_info"):
                await token_service.consume_tokens()
            else:
                raise Exception("Response info not found in request state")

        return response
