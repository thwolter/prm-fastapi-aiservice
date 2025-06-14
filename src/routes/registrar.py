"""
DEPRECATED: This module is deprecated and will be removed in a future version.
Use src.core.routes.validation, src.core.routes.service_handler, and src.core.routes.route_registry instead.
"""

import warnings
from typing import Callable, List, Optional, Type, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel

# Import the new modules
from src.routes.route_registry import RouteRegistry
from src.utils import logutils

TRequest = TypeVar("TRequest", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)

logger = logutils.get_logger(__name__)

# Show deprecation warning
warnings.warn(
    "The registrar module is deprecated. "
    "Use src.core.routes.validation, src.core.routes.service_handler, and src.core.routes.route_registry instead.",
    DeprecationWarning,
    stacklevel=2,
)


class RouteRegistrar:
    """
    DEPRECATED: Use RouteRegistry from src.core.routes.route_registry instead.
    """

    def __init__(self, api_router: APIRouter):
        warnings.warn(
            "RouteRegistrar is deprecated. Use RouteRegistry from src.core.routes.route_registry instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._registry = RouteRegistry(api_router)
        self.router = api_router

    def register_route(
        self,
        path: str,
        request_model: Type[TRequest],
        response_model: Type[TResponse],
        service_factory: Callable[[], object],
        tags: Optional[List[str]] = None,
    ):
        return self._registry.register_route(
            path=path,
            request_model=request_model,
            response_model=response_model,
            service_factory=service_factory,
            tags=tags,
        )


# Create APIRouter instance
router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

# Create route registrar
registrar = RouteRegistrar(router)
