"""
EntitlementService: Manages entitlements via OpenMeter.
"""

from typing import Optional
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError
from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.auth.schemas import EntitlementCreate
from src.utils import logutils
from src.utils.exceptions import ResourceNotFoundException
from src.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class EntitlementService:
    """
    Service for managing entitlements in OpenMeter.
    """

    def __init__(
        self,
        client: Client,
        async_client: AsyncClient,
        request: Optional[Request] = None,
        user_id: Optional[UUID] = None,
    ):
        """
        Initialize the EntitlementService.

        Args:
            client: The OpenMeter client.
            async_client: The async OpenMeter client.
            request: Optional FastAPI request object.
            user_id: Optional UUID of the user. If not provided and request is available, it will be extracted from request.state.
        """
        self.client = client
        self.async_client = async_client
        self.request = request

        self.user_id = user_id

        if request and not user_id:
            self.user_id = request.state.user_id

    @with_resilient_execution(service_name="OpenMeter")
    async def set_entitlement(self, limit: EntitlementCreate) -> None:
        """
        Set an entitlement for a user.

        Args:
            limit: The entitlement details.
        """

        entitlement = {
            "type": "metered",
            "featureKey": limit.feature,
            "issueAfterReset": limit.max_limit,
            "usagePeriod": {"interval": limit.period},
        }

        self.client.create_entitlement(self.user_id, entitlement)

    def set_entitlement_sync(self, limit: EntitlementCreate) -> None:
        """
        Synchronous version of set_entitlement.

        Args:
            limit: The entitlement details.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in the current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.set_entitlement(limit))

    @with_resilient_execution(service_name="OpenMeter")
    async def get_token_entitlement_status(self, feature_key: str) -> bool:
        """
        Check if a user has access to a feature.

        Args:
            feature_key: The feature key to check.

        Returns:
            True if the user has access, False otherwise.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """

        try:
            response = self.client.get_entitlement_value(self.user_id, feature_key)
        except ResourceNotFoundError as e:
            logger.error(f"User {self.user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")

        return bool(response["hasAccess"])

    async def has_access(self, feature_key: str) -> bool:
        """
        Alias for get_token_entitlement_status for backward compatibility.

        Args:
            feature_key: The feature key to check.

        Returns:
            True if the user has access, False otherwise.
        """
        return await self.get_token_entitlement_status(feature_key)

    @with_resilient_execution(service_name="OpenMeter")
    async def get_entitlement_value(self, feature_key: str) -> dict:
        """
        Get the entitlement value for a user.

        Args:
            feature_key: The feature key to check.

        Returns:
            The entitlement value as a dictionary.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        try:
            return self.client.get_entitlement_value(self.user_id, feature_key)
        except ResourceNotFoundError as e:
            logger.error(f"User {self.user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")
