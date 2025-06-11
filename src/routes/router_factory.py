"""Factory for creating routers with routes for all discovered services."""

from src.utils import logutils
from typing import Callable, List, Type, Optional

from fastapi import APIRouter

from src.routes.route_registry import RouteRegistry
from src.services import discover_services

logger = logutils.get_logger(__name__)


def create_router(
    prefix: str = "/api",
    service_discovery_fn: Optional[Callable[[], List[Type]]] = None,
    responses: Optional[dict] = None,
) -> APIRouter:
    """
    Create an APIRouter with routes for all discovered services.

    Args:
        prefix: The prefix for all routes.
        service_discovery_fn: A function that returns a list of service classes.
            If None, the default discover_services function is used.
        responses: A dictionary of responses to include in the router.

    Returns:
        An APIRouter with routes for all discovered services.
    """
    if responses is None:
        responses = {404: {"description": "Not found"}}

    if service_discovery_fn is None:
        service_discovery_fn = discover_services

    # Create the router
    router = APIRouter(
        prefix=prefix,
        responses=responses,
    )

    # Create the registry
    registry = RouteRegistry(router)

    # Discover services
    try:
        services = service_discovery_fn()
        logger.info(f"Discovered {len(services)} services")
    except Exception as e:
        logger.error(f"Error discovering services: {e}")
        services = []

    # Register routes for each service
    for service_class in services:
        try:
            module_parts = service_class.__module__.split(".")
            if len(module_parts) >= 2:
                module_name = module_parts[-2]
            else:
                module_name = module_parts[0] if module_parts else service_class.__name__
            tags = [module_name.capitalize()]

            registry.register_route(
                path=service_class.route_path,  # Use route path defined in the service
                request_model=service_class.QueryModel,
                response_model=service_class.ResultModel,
                service_factory=(lambda cls=service_class: cls()),  # type: ignore
                tags=tags,
            )
            logger.debug(
                f"Registered route for {service_class.__name__} at {service_class.route_path}"
            )
        except Exception as e:
            logger.error(f"Error registering route for {service_class.__name__}: {e}")

    return router
