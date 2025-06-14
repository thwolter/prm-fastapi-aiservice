"""
TokenQuotaServiceProvider: Factory for creating token quota services.
"""

from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.auth.entitlement_service import EntitlementService
from src.auth.subject_service import SubjectService
from src.auth.token_consumption_service import TokenConsumptionService
from src.core.config import settings


class TokenQuotaServiceProvider:
    """
    Provider for token quota services.
    """

    @staticmethod
    def create_clients(request: Request = None):
        """
        Create OpenMeter clients.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A tuple of (sync_client, async_client).
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.OPENMETER_API_KEY}",
        }

        sync_client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers=headers,
        )

        async_client = AsyncClient(
            endpoint=settings.OPENMETER_API_URL,
            headers=headers,
        )

        return sync_client, async_client

    @staticmethod
    def get_customer_service(request: Request = None):
        """
        Get a CustomerService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A CustomerService instance.
        """
        sync_client, async_client = TokenQuotaServiceProvider.create_clients()
        return SubjectService(sync_client, async_client, request)

    @staticmethod
    def get_entitlement_service(request: Request = None):
        """
        Get an EntitlementService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            An EntitlementService instance.
        """
        sync_client, async_client = TokenQuotaServiceProvider.create_clients()
        return EntitlementService(sync_client, async_client, request)

    @staticmethod
    def get_token_consumption_service(request: Request = None):
        """
        Get a TokenConsumptionService instance.

        Args:
            request: Optional FastAPI request object.

        Returns:
            A TokenConsumptionService instance.
        """
        sync_client, async_client = TokenQuotaServiceProvider.create_clients()
        return TokenConsumptionService(sync_client, async_client, request)
