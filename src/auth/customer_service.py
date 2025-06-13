"""
CustomerService: Manages customer operations via OpenMeter.
"""

from typing import Optional
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError
from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.utils import logutils
from src.utils.exceptions import ResourceNotFoundException
from src.utils.resilient import with_resilient_execution

logger = logutils.get_logger(__name__)


class CustomerService:
    """
    Service for managing customers in OpenMeter.
    """

    def __init__(
        self, client: Client, async_client: AsyncClient, request: Optional[Request] = None
    ):
        """
        Initialize the CustomerService.

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
            self.user_email = getattr(request.state, "user_email", None)
        else:
            self.user_id = None
            self.user_email = None

    @property
    def is_local_env(self) -> bool:
        """
        Check if the current environment is local.

        Returns:
            True if the environment is local, False otherwise.
        """
        return settings.ENVIRONMENT == "local"

    @with_resilient_execution(service_name="OpenMeter")
    async def create_customer(
        self, user_id: Optional[UUID] = None, user_email: Optional[str] = None
    ) -> None:
        """
        Create or update a customer in OpenMeter.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.
            user_email: Optional user email. If not provided, uses the email from the request.
        """
        if self.is_local_env:
            logger.debug("Bypassing create_customer in local environment")
            return

        user_id = str(user_id or self.user_id)
        user_email = user_email or self.user_email

        if not user_id:
            logger.error("Cannot create customer: No user ID provided")
            return

        self.client.upsert_subject(
            [
                {
                    "key": user_id,
                    "displayName": user_email,
                }
            ]
        )

    @with_resilient_execution(service_name="OpenMeter")
    async def delete_customer(self, user_id: Optional[UUID] = None) -> None:
        """
        Delete a customer from OpenMeter.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        if self.is_local_env:
            logger.debug("Bypassing delete_customer in local environment")
            return

        user_id = str(user_id or self.user_id)

        if not user_id:
            logger.error("Cannot delete customer: No user ID provided")
            return

        try:
            self.client.delete_subject(user_id)
        except ResourceNotFoundError as e:
            logger.error(f"User {user_id} not found for deletion: {e}")
            raise ResourceNotFoundException(detail="User not found")
