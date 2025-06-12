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

import asyncio
import uuid
from typing import Any
from uuid import UUID

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.rest import HttpRequest
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.auth.schemas import ConsumedTokensInfo
from src.core.config import settings
from src.utils import logutils
from src.utils.exceptions import RequestException, ResourceNotFoundException
from src.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class TokenQuotaService:
    def __init__(self, request: Request):
        self.request = request

        if self.is_local_env:
            self.auth_token = getattr(self.request.state, "token", "dummy_token")
            self.user_id = getattr(
                self.request.state, "user_id", "00000000-0000-0000-0000-000000000000"
            )
        else:
            self.auth_token = self.request.state.token
            self.user_id = self.request.state.user_id

        self.client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.OPENMETER_API_KEY}",
            },
        )

        self._reserved_tokens: int = 0

    @property
    def is_local_env(self) -> bool:
        return settings.ENVIRONMENT == "local"

    async def get_token_entitlement_status(self) -> bool:
        """
        Returns True if the user has a positive token entitlement.
        In local environment, always returns True (bypassed for dev/testing).
        """
        if self.is_local_env:
            logger.debug("Bypassing token entitlement check in local environment")
            return True

        try:
            response = self.client.get_entitlement_value(str(self.user_id), "ai_tokens")
        except ResourceNotFoundError as e:
            logger.error(f"User {self.user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")
        return bool(response["hasAccess"])

    @with_resilient_execution(service_name="OpenMeter")
    async def decrement_entitlement(self, tokens: int) -> bool:
        """
        Atomically checks the user's entitlement and decrements by 'tokens' if possible.
        Returns True if successful, False otherwise.
        """
        if self.is_local_env:
            logger.debug("Bypassing decrement_entitlement in local environment")
            return True

        async_client = AsyncClient(
            endpoint=settings.OPENMETER_API_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.OPENMETER_API_KEY}",
            },
        )

        request = HttpRequest(
            method="POST",
            url=f"/api/v1/subjects/{self.user_id}/entitlements/ai_tokens/check-and-decrement",
            json={"amount": tokens},
        )

        try:
            response = await asyncio.wait_for(async_client.send_request(request), timeout=1.0)
            if response.status_code == 200:
                return True
            if response.status_code in (402, 403, 409):
                return False
            response.raise_for_status()
        except (HttpResponseError, ResourceNotFoundError) as e:
            logger.error(f"OpenMeter decrement_entitlement failed: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise ResourceNotFoundException(detail="User not found")
            raise
        finally:
            await async_client.close()

        return False

    async def reserve_token_quota(self, tokens: int) -> bool:
        """
        Reserve (pre-consume) an estimated number of tokens for the user.
        Returns True if reservation is successful.
        """
        success = await self.decrement_entitlement(tokens)
        if success:
            self._reserved_tokens = tokens
        return success

    @with_resilient_execution(service_name="OpenMeter")
    async def adjust_consumed_tokens(self, result: Any, user_id: UUID) -> None:
        """
        Adjust the reserved tokens based on actual usage by sending a CloudEvent.
        The adjustment is the difference between actual and reserved tokens.
        """
        if self.is_local_env:
            logger.debug("Bypassing adjust_consumed_tokens in local environment")
            if hasattr(result, "tokens_info"):
                del result.tokens_info
            self._reserved_tokens = 0
            return

        try:
            payload = ConsumedTokensInfo(**result.tokens_info)
            del result.tokens_info
        except ValueError as e:
            logger.error(f"Invalid tokens info: {e}")
            raise RequestException(detail="Invalid tokens info")

        diff = payload.total_tokens - self._reserved_tokens
        if diff == 0:
            self._reserved_tokens = 0
            return

        event_data = {
            "tokens": diff,
            "model": payload.model_name,
            "prompt": payload.prompt_name,
        }
        response_info = getattr(result, "response_info", None)
        if response_info is not None:
            event_data["response_info"] = response_info

        event = CloudEvent(
            attributes={
                "id": str(uuid.uuid4()),
                "type": "tokens",
                "source": settings.OPENMETER_SOURCE,
                "subject": str(user_id),
            },
            data=event_data,
        )

        self.client.ingest_events(to_dict(event))
        self._reserved_tokens = 0
