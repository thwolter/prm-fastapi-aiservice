"""
TokenConsumptionService: Manages token consumption via OpenMeter.
"""

import asyncio
import uuid
from typing import Any, Optional
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


class TokenConsumptionService:
    """
    Service for managing token consumption in OpenMeter.
    """

    def __init__(
        self, client: Client, async_client: AsyncClient, request: Optional[Request] = None
    ):
        """
        Initialize the TokenConsumptionService.

        Args:
            client: The OpenMeter client.
            async_client: The async OpenMeter client.
            request: Optional FastAPI request object.
        """
        self.client = client
        self.async_client = async_client
        self.request = request

        if request:
            self.user_id = request.state.user_id
        else:
            self.user_id = None

        self._reserved_tokens: int = 0

    @property
    def is_local_env(self) -> bool:
        """
        Check if the current environment is local.

        Returns:
            True if the environment is local, False otherwise.
        """
        return settings.ENVIRONMENT == "local"

    @with_resilient_execution(service_name="OpenMeter")
    async def decrement_entitlement(self, tokens: int, user_id: Optional[UUID] = None) -> bool:
        """
        Atomically checks the user's entitlement and decrements by 'tokens' if possible.

        Args:
            tokens: The number of tokens to decrement.
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Returns:
            True if successful, False otherwise.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        if self.is_local_env:
            logger.debug("Bypassing decrement_entitlement in local environment")
            return True

        user_id = str(user_id or self.user_id)

        if not user_id:
            logger.error("Cannot decrement entitlement: No user ID provided")
            return False

        request = HttpRequest(
            method="POST",
            url=f"/subjects/{user_id}/entitlements/ai_tokens/check-and-decrement",
            json={"amount": tokens},
        )

        try:
            response = await asyncio.wait_for(
                self.async_client.send_request(request), timeout=settings.OPENMETER_TIMEOUT
            )
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

        return False

    @with_resilient_execution(service_name="OpenMeter")
    async def reserve_token_quota(self, tokens: int, user_id: Optional[UUID] = None) -> bool:
        """
        Reserve (pre-consume) an estimated number of tokens for the user.

        Args:
            tokens: The number of tokens to reserve.
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Returns:
            True if reservation is successful.
        """
        user_id = user_id or self.user_id
        success = await self.decrement_entitlement(tokens, user_id)
        if success:
            self._reserved_tokens = tokens
        return success

    @with_resilient_execution(service_name="OpenMeter")
    async def adjust_consumed_tokens(self, result: Any, user_id: Optional[UUID] = None) -> None:
        """
        Adjust the reserved tokens based on actual usage by sending a CloudEvent.
        The adjustment is the difference between actual and reserved tokens.

        Args:
            result: The result object containing token information.
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Raises:
            RequestException: If the token information is invalid.
        """
        if self.is_local_env:
            logger.debug("Bypassing adjust_consumed_tokens in local environment")
            if hasattr(result, "tokens_info"):
                del result.tokens_info
            self._reserved_tokens = 0
            return

        user_id = user_id or self.user_id

        if not user_id:
            logger.error("Cannot adjust consumed tokens: No user ID provided")
            return

        # Convert UUID to string if it's not already a string
        user_id_str = str(user_id)

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
                "subject": user_id_str,
            },
            data=event_data,
        )

        self.client.ingest_events(to_dict(event))
        self._reserved_tokens = 0

    async def consume_tokens(self, result: Any, user_id: Optional[UUID] = None) -> None:
        """
        Alias for adjust_consumed_tokens for backward compatibility.

        Args:
            result: The result object containing token information.
            user_id: Optional user ID. If not provided, uses the ID from the request.
        """
        await self.adjust_consumed_tokens(result, user_id)
