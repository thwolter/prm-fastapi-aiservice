import inspect
import importlib
import pkgutil

from fastapi import APIRouter

from src.core.registrar import RouteRegistrar

# Discover all ``service`` modules within the ``src`` package so that
# newly added wrappers are registered automatically without having to
# modify this file.
services = []
for _, module_name, _ in pkgutil.walk_packages(
    path=importlib.import_module('src').__path__, prefix='src.'
):
    if not module_name.split('.')[-1].endswith('service'):
        continue
    module = importlib.import_module(module_name)
    services.extend(
        member
        for _, member in inspect.getmembers(module, inspect.isclass)
        if getattr(member, 'route_path', None)
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

