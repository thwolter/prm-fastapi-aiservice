"""
Middleware for checking token entitlements before processing requests.
"""

from typing import Optional
from uuid import UUID

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenEntitlementCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware that checks if a user has sufficient tokens before processing a request.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Check if the user has sufficient tokens before processing the request.

        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint handler.

        Returns:
            The response from the next middleware or endpoint handler,
            or a 403 Forbidden response if the user doesn't have sufficient tokens.
        """
        # Skip token check for non-API routes or if no user ID is available
        if not request.url.path.startswith("/api") or not hasattr(request.state, "user_id"):
            return await call_next(request)

        user_id: Optional[UUID] = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        # Get the token entitlement service
        token_service = TokenQuotaServiceProvider.get_entitlement_service(request)

        # Check if the user has access to the tokens feature
        feature_key = settings.OPENMETER_FEATURE_KEY
        try:
            # Get the entitlement value to check the balance
            entitlement = await token_service.get_entitlement_value(user_id, feature_key)

            has_access = entitlement.get("hasAccess", False)
            if not has_access:
                logger.warning(f"User {user_id} does not have access to feature {feature_key}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Insufficient token entitlement. Please check your subscription."
                    },
                )

            if entitlement["balance"] <= 0:
                logger.warning(
                    f"User {user_id} has insufficient token balance: {entitlement['balance']}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Insufficient token balance. Please add more tokens to your account."
                    },
                )

        except Exception as e:
            logger.error(f"Error checking token entitlement for user {user_id}: {e}")
            # Allow the request to proceed in case of errors checking entitlement
            # This is a fail-open approach to prevent blocking legitimate requests
            return await call_next(request)

        # User has sufficient tokens, proceed with the request
        return await call_next(request)
