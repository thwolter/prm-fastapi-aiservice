import inspect

from fastapi import APIRouter

from app.category import service as category_service
from app.core.registrar import RouteRegistrar
from app.project import service as project_service
from app.risk import service as risk_service

# Dynamically import services from the specified module
modules = [
    category_service,
    project_service,
    risk_service,
]
services = []

# Dynamically import services from the specified modules
for module in modules:
    # Filter out the service classes
    services.extend(
        member
        for name, member in inspect.getmembers(module, inspect.isclass)
        if member.__module__ == module.__name__
    )

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
