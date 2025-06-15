"""
CustomerService: Manages customer operations via OpenMeter.
"""

from typing import List, Optional
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


class SubjectService:
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
    async def create_subject(
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

        subj = {"key": user_id, "displayName": user_email}
        self.client.upsert_subject([subj])

    def create_subject_sync(
        self, user_id: Optional[UUID] = None, user_email: Optional[str] = None
    ) -> None:
        """
        Synchronous version of create_subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.
            user_email: Optional user email. If not provided, uses the email from the request.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.create_subject(user_id, user_email))

    @with_resilient_execution(service_name="OpenMeter")
    async def delete_subject(self, user_id: Optional[UUID] = None) -> None:
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

    def delete_subject_sync(self, user_id: Optional[UUID] = None) -> None:
        """
        Synchronous version of delete_subject.

        Args:
            user_id: Optional user ID. If not provided, uses the ID from the request.

        Raises:
            ResourceNotFoundException: If the user is not found.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.delete_subject(user_id))

    @with_resilient_execution(service_name="OpenMeter")
    async def list_subjects_without_entitlement(self) -> List[UUID]:
        """
        List all subjects without an entitlement.

        Note: This implementation assumes that the OpenMeter client provides methods
        like `list_subjects()` and `list_entitlements(subject_id)`. If these methods
        don't exist, this implementation will need to be modified.

        Returns:
            A list of UUIDs of subjects without entitlements.
        """
        if self.is_local_env:
            logger.debug("Bypassing list_subjects_without_entitlement in local environment")
            return []

        # Get all subjects
        # Note: This assumes that the OpenMeter client has a list_subjects() method
        subjects = self.client.list_subjects()

        # Filter subjects without entitlements
        subjects_without_entitlement = []
        for subject in subjects:
            try:
                # Check if subject has any entitlements
                # Note: This assumes that the OpenMeter client has a list_entitlements(subject_id) method
                entitlements = self.client.list_entitlements(subject=[str(subject["key"])])
                if not entitlements:
                    subjects_without_entitlement.append(UUID(subject["key"]))
            except ResourceNotFoundError:
                # If no entitlements found, add to the list
                subjects_without_entitlement.append(UUID(subject["key"]))
        logger.debug(f"Found {len(subjects_without_entitlement)} subjects without entitlements")

        return subjects_without_entitlement

    def list_subjects_without_entitlement_sync(self) -> List[UUID]:
        """
        Synchronous version of list_subjects_without_entitlement.

        Returns:
            A list of UUIDs of subjects without entitlements.
        """
        import asyncio

        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.list_subjects_without_entitlement())
