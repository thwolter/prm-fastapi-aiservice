"""
TokenQuotaService: Manages token consumption and entitlements via OpenMeter.

GRANT STRATEGY (recommended for alignment with monthly entitlements):

- Configure OpenMeter entitlements with a monthly reset (usagePeriod = MONTH).
- Issue recurring grants at the start of each month for each user, matching the monthly token allowance.
- Token consumption process:
    1. Reserve estimated tokens at request start (atomic decrement of entitlement).
    2. After actual usage is known, adjust the consumed tokens with a CloudEvent reflecting the true usage (adjustment event).
    3. All token consumption and adjustments occur within the same monthly entitlement period.

Example (pseudo-code for entitlement/grant setup):

openmeter.subjects.createEntitlement('user-id', {
    type: 'metered',
    featureKey: 'ai_tokens',
    usagePeriod: { interval: 'MONTH' },
    issueAfterReset: monthly_limit,
    isSoftLimit: False
})

# See OpenMeter documentation for detailed configuration.
"""

from typing import Any
from uuid import UUID

from fastapi import Request

from src.auth.schemas import EntitlementCreate
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenQuotaService:
    """
    Legacy service that delegates to specialized services.
    This class is maintained for backward compatibility.

    For new code, use the specialized services directly:
    - CustomerService: For customer management
    - EntitlementService: For entitlement management
    - TokenConsumptionService: For token consumption
    """

    def __init__(self, request: Request):
        self.request = request

        self.auth_token = self.request.state.token
        self.user_id = self.request.state.user_id
        self.user_email = getattr(self.request.state, "user_email", None)

        # Create specialized services
        self.customer_service = TokenQuotaServiceProvider.get_customer_service(request)
        self.entitlement_service = TokenQuotaServiceProvider.get_entitlement_service(request)
        self.token_service = TokenQuotaServiceProvider.get_token_consumption_service(request)

    @property
    def is_local_env(self) -> bool:
        return self.customer_service.is_local_env

    async def create_customer(self, user_id: UUID = None):
        """
        Create or update a customer in OpenMeter.
        Delegates to CustomerService.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.
        """
        await self.customer_service.create_customer(user_id)

    async def delete_customer(self):
        """
        Deletes the user from OpenMeter.
        This is typically used during user deletion or cleanup.
        Delegates to CustomerService.
        """
        await self.customer_service.delete_customer()

    async def set_entitlement(self, limit: EntitlementCreate, user_id: UUID = None):
        """
        Set an entitlement for a user.
        Delegates to EntitlementService.

        Args:
            limit: The entitlement details.
            user_id: Optional user ID. If not provided, uses the ID from the request.
        """
        await self.entitlement_service.set_entitlement(limit, user_id)

    async def get_token_entitlement_status(self) -> bool:
        """
        Returns True if the user has a positive token entitlement.
        In local environment, always returns True (bypassed for dev/testing).
        Delegates to EntitlementService.
        """
        return await self.entitlement_service.get_token_entitlement_status()

    async def has_access(self) -> bool:
        """
        Alias for get_token_entitlement_status.
        """
        return await self.get_token_entitlement_status()

    async def decrement_entitlement(self, tokens: int) -> bool:
        """
        Atomically checks the user's entitlement and decrements by 'tokens' if possible.
        Returns True if successful, False otherwise.
        Delegates to TokenConsumptionService.
        """
        return await self.token_service.decrement_entitlement(tokens)

    async def reserve_token_quota(self, tokens: int, user_id: UUID = None) -> bool:
        """
        Reserve (pre-consume) an estimated number of tokens for the user.
        Returns True if reservation is successful.
        Delegates to TokenConsumptionService.

        Args:
            tokens: The number of tokens to reserve.
            user_id: Optional user ID. If not provided, uses the ID from the request.
        """
        return await self.token_service.reserve_token_quota(tokens, user_id)

    async def adjust_consumed_tokens(self, result: Any, user_id: UUID) -> None:
        """
        Adjust the reserved tokens based on actual usage by sending a CloudEvent.
        The adjustment is the difference between actual and reserved tokens.
        Delegates to TokenConsumptionService.
        """
        await self.token_service.adjust_consumed_tokens(result, user_id)

    async def consume_tokens(self, result: Any, user_id: UUID) -> None:
        """
        Alias for adjust_consumed_tokens.
        """
        await self.adjust_consumed_tokens(result, user_id)

    async def get_entitlement_value(self, user_id: UUID, feature_key: str = "ai_tokens") -> dict:
        """
        Get the entitlement value for a user.
        Delegates to EntitlementService.
        """
        return await self.entitlement_service.get_entitlement_value(user_id, feature_key)
