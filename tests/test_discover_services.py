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
        print(f"Found module: {module_name}")
        if not (module_name.split('.')[-1].endswith('service') or module_name.split('.')[-1].endswith('services')):
            continue
        print(f"Processing module: {module_name}")
        module = importlib.import_module(module_name)
        for name, member in inspect.getmembers(module, inspect.isclass):
            if getattr(member, 'route_path', None):
                print(f"Found service: {name} with route_path: {member.route_path}")
                services.append(member)
    return services

if __name__ == "__main__":
    services = discover_services()
    print(f"Discovered {len(services)} services:")
    for service in services:
        print(f"  - {service.__name__} with route_path: {service.route_path}")
