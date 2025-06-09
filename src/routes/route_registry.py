"""Route registry for registering API routes."""
from src.utils import logutils
from typing import Callable, List, Optional, Type, TypeVar

from fastapi import APIRouter, Body, Depends, Request
from pydantic import BaseModel

from src.auth.dependencies import get_current_user
from src.auth.service import TokenService
from src.routes.service_handler import ServiceHandler
from src.utils.exceptions import BaseServiceException, QuotaExceededException

TRequest = TypeVar('TRequest', bound=BaseModel)
TResponse = TypeVar('TResponse', bound=BaseModel)

logger = logutils.get_logger(__name__)


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
        service_factory: Callable[[], object],
        tags: Optional[List[str]] = None,
        auth_dependency: Optional[Callable] = None,
    ):
        """
        Register a route with the FastAPI router.

        Args:
            path: The URL path for the route.
            request_model: The Pydantic model for the request.
            response_model: The Pydantic model for the response.
            service_factory: A callable that returns a service instance.
            tags: Optional list of tags for the route.
            auth_dependency: Optional custom authentication dependency.
                If None, the default get_current_user dependency is used.
        """
        # Create a service handler for this route
        handler = ServiceHandler(service_factory, request_model, response_model)

        # Use the provided auth dependency or the default
        auth_dep = auth_dependency or get_current_user

        async def route_function(
            request: Request,
            request_model: request_model = Body(..., embed=False),
            user_info: dict = Depends(auth_dep),
        ) -> response_model:
            """
            Route handler function.

            Args:
                request: The FastAPI request object.
                request_model: The request data.
                user_info: User information from authentication.

            Returns:
                The response data.

            Raises:
                BaseServiceException: If an error occurs during processing.
            """
            # Check token quota
            user_id = user_info['user_id']
            token_service = TokenService(request)
            has_access = await token_service.has_access()
            if not has_access:
                raise QuotaExceededException(detail='Token quota exceeded')

            # Handle the request
            result = await handler.handle(request_model)

            # Consume tokens
            await token_service.consume_tokens(result, user_id)

            return result

        # Register the route with the FastAPI router
        self.router.post(
            path, 
            response_model=response_model, 
            tags=tags
        )(route_function)

        logger.debug(f"Registered route: {path} with tags: {tags}")
