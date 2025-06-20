"""
EntitlementService: Manages entitlements.
"""

from typing import Optional
from uuid import UUID

from fastapi import Request

from src.domain.models import Entitlement
from src.external.entitlements.abstract_entitlement_client import AbstractEntitlementClient
from src.utils import logutils
from src.utils.resilient import with_resilient_execution
from utils.context_managers import handle_resource_not_found

logger = logutils.get_logger(__name__)


class EntitlementService:
    """
    Service for managing entitlements.
    """

    def __init__(
        self,
        entitlement_client: AbstractEntitlementClient,
        request: Optional[Request] = None,
        user_id: Optional[UUID] = None,
    ):
        """
        Initialize the EntitlementService.

        Args:
            entitlement_client: The entitlement client.
            request: Optional FastAPI request object.
            user_id: Optional UUID of the user. If not provided and request is available, it will be extracted from request.state.
        """
        self.entitlement_client = entitlement_client
        self.request = request

        self.user_id = user_id

        if request and not user_id:
            self.user_id = request.state.user_id

    @with_resilient_execution(service_name='EntitlementService')
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

        with handle_resource_not_found(self.user_id):
            entitlement = self.entitlement_client.get_entitlement_value(
                str(self.user_id), feature_key
            )
            return entitlement.has_access

    async def has_access(self, feature_key: str) -> bool:
        """
        Alias for get_token_entitlement_status for backward compatibility.

        Args:
            feature_key: The feature key to check.

        Returns:
            True if the user has access, False otherwise.
        """
        return await self.get_token_entitlement_status(feature_key)

    @with_resilient_execution(service_name='EntitlementService')
    async def get_entitlement_value(self, feature_key: str) -> Entitlement:
        """
        Get the entitlement value for a user.

        Args:
            feature_key: The feature key to check.

        Returns:
            The entitlement value.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        with handle_resource_not_found(self.user_id):
            return self.entitlement_client.get_entitlement_value(str(self.user_id), feature_key)
