import importlib
import inspect
import pkgutil
from typing import Type


def discover_services() -> list[Type]:
    """Discover all service classes within the ``src`` package."""
    services: list[Type] = []
    for _, module_name, _ in pkgutil.walk_packages(
        importlib.import_module('src').__path__, prefix='src.'
    ):
        if not (module_name.split('.')[-1].endswith('service') or module_name.split('.')[-1].endswith('services')):
            continue
        module = importlib.import_module(module_name)
        services.extend(
            member
            for _, member in inspect.getmembers(module, inspect.isclass)
            if getattr(member, 'route_path', None)
        )
    return services
