"""Route registry for registering API routes."""

from enum import Enum
from typing import Annotated, Callable, List, Optional, Type, TypeVar, Union

from fastapi import APIRouter, Body, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.core.config import settings
from src.routes.service_handler import ServiceHandler, ServiceProtocol
from src.utils import logutils
from src.utils.exceptions import QuotaExceededException

TRequest = TypeVar("TRequest", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)

logger = logutils.get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=True)


class RouteRegistry:
    """
    Registry for API routes.

    This class is responsible for registering routes with a FastAPI router.
    It handles:
    1. Creating a service handler for each route
    2. Setting up authentication and token quota checking
    3. Registering the route with the FastAPI router
    """

    def __init__(self, api_router: APIRouter):
        """
        Initialize the route registry.

        Args:
            api_router: The FastAPI router to register routes with.
        """
        self.router = api_router

    def register_route(
        self,
        path: str,
        request_model: Type[TRequest],
        response_model: Type[TResponse],
        service_factory: Callable[[], ServiceProtocol],
        tags: Optional[List[Union[str, Enum]]] = None,
    ) -> None:
        """
        Register a route with the FastAPI router.

        Args:
            path: The URL path for the route.
            request_model: The Pydantic model for the request.
            response_model: The Pydantic model for the response.
            service_factory: A callable that returns a service instance.
            tags: Optional list of tags for the route.
        """
        # Create a service handler for this route
        handler = ServiceHandler(service_factory, request_model, response_model)

        # Define a route function that bypasses authentication and metering in local environment
        if settings.ENVIRONMENT == "local":

            async def route_function(
                request: Request,
                token: Annotated[str, Depends(bearer_scheme)],
                request_model: request_model = Body(..., embed=False),  # type: ignore[valid-type]
            ) -> response_model:  # type: ignore[valid-type]
                """
                Route handler function for local environment (no auth/metering).

                Args:
                    request: The FastAPI request object.
                    token: The authentication token from the request.
                    request_model: The request data.

                Returns:
                    The response data.

                Raises:
                    BaseServiceException: If an error occurs during processing.
                """
                logger.debug("Local environment: Bypassing authentication and metering")

                # Handle the request without authentication or metering
                result = await handler.handle(request_model)

                return result

        else:

            async def route_function(
                request: Request,
                token: Annotated[str, Depends(bearer_scheme)],
                request_model: request_model = Body(..., embed=False),  # type: ignore[valid-type]
            ) -> response_model:  # type: ignore[valid-type]
                """
                Route handler function with authentication and metering.

                Args:
                    request: The FastAPI request object.
                    token: The authentication token from the request.
                    request_model: The request data.

                Returns:
                    The response data.

                Raises:
                    BaseServiceException: If an error occurs during processing.
                """

                print(f"Received request for {request.url.path} with token: {token}")
                # Check token quota
                user_id = request.state.user_id
                entitlement_service = TokenQuotaServiceProvider.get_entitlement_service(request)
                token_service = TokenQuotaServiceProvider.get_token_consumption_service(request)

                has_access = await entitlement_service.has_access()
                if not has_access:
                    raise QuotaExceededException(detail="Token quota exceeded")

                # Handle the request
                handler.set_request(request)
                result = await handler.handle(request_model)

                # Consume tokens
                await token_service.consume_tokens(result, user_id)

                return result

        # Register the route with the FastAPI router
        self.router.post(
            path,
            response_model=response_model,
            tags=tags,
        )(route_function)

        logger.debug(f"Registered route: {path} with tags: {tags}")
