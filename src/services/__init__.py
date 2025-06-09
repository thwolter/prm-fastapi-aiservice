import importlib
import inspect
import logging
import pkgutil
from typing import Type, List, Optional

logger = logging.getLogger(__name__)

def discover_services() -> List[Type]:
    """
    Discover all service classes within the ``src`` package.

    This function walks through all modules in the src package, looking for service classes.
    A service class is identified by having a 'route_path' attribute.

    Returns:
        List[Type]: A list of service classes discovered in the project.
    """
    services: List[Type] = []

    try:
        # Get the src package
        src_package = importlib.import_module('src')
        logger.debug(f"Starting service discovery in package: src")

        # Walk through all modules in the src package
        for _, module_name, is_pkg in pkgutil.walk_packages(
            src_package.__path__, prefix='src.'
        ):
            # Skip modules that don't look like service modules
            module_basename = module_name.split('.')[-1]
            if not (module_basename.endswith('service') or module_basename.endswith('services')):
                continue

            logger.debug(f"Found potential service module: {module_name}")

            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Find all classes in the module that have a route_path attribute
                for name, member in inspect.getmembers(module, inspect.isclass):
                    route_path: Optional[str] = getattr(member, 'route_path', None)
                    if route_path:
                        logger.debug(f"Found service: {name} with route_path: {route_path}")
                        services.append(member)

            except ImportError as e:
                logger.error(f"Error importing module {module_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing module {module_name}: {e}")

    except ImportError as e:
        logger.error(f"Error importing src package: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during service discovery: {e}")

    logger.info(f"Discovered {len(services)} services")
    return services
