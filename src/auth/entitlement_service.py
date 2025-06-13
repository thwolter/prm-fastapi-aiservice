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
from src.core.config import settings
from src.utils import logutils
from src.utils.exceptions import ResourceNotFoundException
from src.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class EntitlementService:
    """
    Service for managing entitlements in OpenMeter.
    """

    def __init__(
        self, client: Client, async_client: AsyncClient, request: Optional[Request] = None
    ):
        """
        Initialize the EntitlementService.

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

    @property
    def is_local_env(self) -> bool:
        """
        Check if the current environment is local.

        Returns:
            True if the environment is local, False otherwise.
        """
        return settings.ENVIRONMENT == "local"

    @with_resilient_execution(service_name="OpenMeter")
    async def set_entitlement(
        self, limit: EntitlementCreate, user_id: Optional[UUID] = None
    ) -> None:
        """
        Set an entitlement for a user.

        Args:
            limit: The entitlement details.
            user_id: Optional user ID. If not provided, uses the ID from the request.
        """
        if self.is_local_env:
            logger.debug("Bypassing set_entitlement in local environment")
            return

        user_id = str(user_id or self.user_id)

        if not user_id:
            logger.error("Cannot set entitlement: No user ID provided")
            return

        entitlement = {
            "type": "metered",
            "featureKey": limit.feature,
            "issueAfterReset": limit.max_limit,
            "usagePeriod": {"interval": limit.period},
        }

        self.client.create_entitlement(user_id, entitlement)

    @with_resilient_execution(service_name="OpenMeter")
    async def get_token_entitlement_status(
        self, feature_key: str = "ai_tokens", user_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if a user has access to a feature.

        Args:
            feature_key: The feature key to check.
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Returns:
            True if the user has access, False otherwise.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        if self.is_local_env:
            logger.debug("Bypassing token entitlement check in local environment")
            return True

        user_id = str(user_id or self.user_id)

        if not user_id:
            logger.error("Cannot check entitlement: No user ID provided")
            return False

        try:
            response = self.client.get_entitlement_value(user_id, feature_key)
        except ResourceNotFoundError as e:
            logger.error(f"User {user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")

        return bool(response["hasAccess"])

    async def has_access(
        self, feature_key: str = "ai_tokens", user_id: Optional[UUID] = None
    ) -> bool:
        """
        Alias for get_token_entitlement_status for backward compatibility.

        Args:
            feature_key: The feature key to check.
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Returns:
            True if the user has access, False otherwise.
        """
        return await self.get_token_entitlement_status(feature_key, user_id)

    @with_resilient_execution(service_name="OpenMeter")
    async def get_entitlement_value(self, user_id: UUID, feature_key: str = "ai_tokens") -> dict:
        """
        Get the entitlement value for a user.

        Args:
            user_id: The user ID.
            feature_key: The feature key to check.

        Returns:
            The entitlement value as a dictionary.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        if self.is_local_env:
            logger.debug("Bypassing get_entitlement_value in local environment")
            return {"hasAccess": True, "balance": 1000}

        user_id = str(user_id)

        try:
            return self.client.get_entitlement_value(user_id, feature_key)
        except ResourceNotFoundError as e:
            logger.error(f"User {user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")
