# src/middleware/service_bypass.py
from typing import Any, Dict, Type

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)

# Registry of services that should be bypassed in local environments
service_registry: Dict[str, Type] = {}


def register_service(service_name: str, service_class: Type) -> None:
    """Register a service to be bypassed in local environments."""
    service_registry[service_name] = service_class


class ServiceBypassMiddleware(BaseHTTPMiddleware):
    """
    Middleware to bypass services in local environments.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        If in local environment, replace registered services with mock implementations.
        """
        if settings.ENVIRONMENT == "local":
            logger.debug("Local environment: bypassing registered services")

            # Store original service implementations
            original_services = {}

            # Replace services with mock implementations
            for service_name, service_class in service_registry.items():
                original_services[service_name] = getattr(request.app.state, service_name, None)

                # Create a mock implementation
                mock_service = self._create_mock_service(service_class)
                setattr(request.app.state, service_name, mock_service)

            # Process the request
            response = await call_next(request)

            # Restore original service implementations
            for service_name, original_service in original_services.items():
                setattr(request.app.state, service_name, original_service)

            return response

        return await call_next(request)

    def _create_mock_service(self, service_class: Type) -> Any:
        """
        Create a mock implementation of a service.
        This could be customized based on the service type.
        """

        # Basic implementation that returns default values
        class MockService:
            async def set_entitlement(self, *args, **kwargs):
                logger.debug("Bypassing set_entitlement in local environment")
                return None

            async def get_token_entitlement_status(self, *args, **kwargs):
                logger.debug("Bypassing get_token_entitlement_status in local environment")
                return True

            async def get_entitlement_value(self, *args, **kwargs):
                logger.debug("Bypassing get_entitlement_value in local environment")
                return {"hasAccess": True, "balance": 1000}

            async def create_subject(self, *args, **kwargs):
                logger.debug("Bypassing create_subject in local environment")
                return None

            async def delete_subject(self, *args, **kwargs):
                logger.debug("Bypassing delete_subject in local environment")
                return None

            async def list_subjects_without_entitlement(self, *args, **kwargs):
                logger.debug("Bypassing list_subjects_without_entitlement in local environment")
                return []

            # Add other methods as needed

        return MockService()
