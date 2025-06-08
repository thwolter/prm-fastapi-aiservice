from src.services import discover_services

from fastapi import APIRouter

from src.core.registrar import RouteRegistrar

# Automatically discover service classes from the ``services`` package.
services = discover_services()

router = APIRouter(
    prefix='/api',
    responses={404: {'description': 'Not found'}},
)

registrar = RouteRegistrar(router)

for service_class in services:
    module_name = service_class.__module__.split('.')[-2]
    tags = [module_name.capitalize()]

    registrar.register_route(
        path=service_class.route_path,  # Use route path defined in the service
        request_model=service_class.QueryModel,
        response_model=service_class.ResultModel,
        service_factory=lambda cls=service_class: cls(),  # Dynamically instantiate
        tags=tags,
    )

