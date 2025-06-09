# Services and Routes

This document explains how services and routes are defined, discovered, and registered in the AI Service project.

## Service Definition

Services in the AI Service project are defined as classes that inherit from `BaseService` in `src/services/base_service.py`. Each service class must define the following attributes:

- `chain_fn`: A callable that implements the service's functionality
- `route_path`: A string that defines the API endpoint for the service
- `QueryModel`: A Pydantic model that defines the structure of the request data
- `ResultModel`: A Pydantic model that defines the structure of the response data

Here's an example of a service definition from `src/services/services.py`:

```python
class RiskIdentificationService(BaseService):
    """Service for identifying risks."""

    chain_fn = chains.async_get_risks_chain
    route_path = '/risk/identify/'
    QueryModel = rg_schemas.RiskRequest
    ResultModel = rg_schemas.RiskResponse
```

## Service Discovery

Services are automatically discovered by the `discover_services` function in `src/services/__init__.py`. This function:

1. Walks through all modules in the `src` package
2. Looks for modules with names ending in 'service' or 'services'
3. Imports these modules and finds all classes that have a `route_path` attribute
4. Returns a list of these service classes

Here's how the service discovery works:

```python
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
```

## Route Registration

Routes are registered in `src/router.py` using the `create_router` function from `src/core/routes/router_factory.py`. The process works as follows:

1. The `create_router` function is called to create a router with routes for all discovered services
2. Inside `create_router`:
   - An `APIRouter` instance is created with the specified prefix
   - A `RouteRegistry` instance is created with the router
   - The `discover_services` function is called to get a list of service classes
   - For each service class, a route is registered using the `register_route` method

Here's the relevant code from `src/router.py`:

```python
from routes import create_router

# Create a router with routes for all discovered services
router = create_router()
```

And here's how the `create_router` function works:

```python
def create_router(
    prefix: str = '/api',
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
        responses = {404: {'description': 'Not found'}}

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
            module_name = service_class.__module__.split('.')[-2]
            tags = [module_name.capitalize()]

            registry.register_route(
                path=service_class.route_path,  # Use route path defined in the service
                request_model=service_class.QueryModel,
                response_model=service_class.ResultModel,
                service_factory=lambda cls=service_class: cls(),  # Dynamically instantiate
                tags=tags,
            )
            logger.debug(f"Registered route for {service_class.__name__} at {service_class.route_path}")
        except Exception as e:
            logger.error(f"Error registering route for {service_class.__name__}: {e}")

    return router
```

The `RouteRegistry.register_route` method creates a FastAPI route handler that:

1. Creates a `ServiceHandler` for the service
2. Sets up authentication using the provided dependency or the default
3. Defines a route function that:
   - Authenticates the user and checks token quota
   - Handles the request using the service handler
   - Consumes tokens based on the response
   - Returns the validated response
4. Registers the route function with the FastAPI router

## Core Components

The route registration system is built on several core components:

### Validation

The `src/core/routes/validation.py` module provides utilities for validating request and response data against Pydantic models.

### Service Handler

The `src/core/routes/service_handler.py` module provides the `ServiceHandler` class, which is responsible for:

1. Creating a service instance using the provided factory
2. Executing the service query
3. Validating the response
4. Handling errors

### Route Registry

The `src/core/routes/route_registry.py` module provides the `RouteRegistry` class, which is responsible for:

1. Creating a service handler for each route
2. Setting up authentication and token quota checking
3. Registering the route with the FastAPI router

## Adding a New Service

To add a new service to the AI Service project:

1. Create a new class that inherits from `BaseService`
2. Define the required attributes: `chain_fn`, `route_path`, `QueryModel`, and `ResultModel`
3. Place the class in a module with a name ending in 'service' or 'services'

The service will be automatically discovered and registered when the application starts.

Example:

```python
from src.services.base_service import BaseService
from riskgpt import chains
from riskgpt.models import schemas as rg_schemas

class MyNewService(BaseService):
    """Service for my new functionality."""

    chain_fn = chains.async_my_new_chain
    route_path = '/my/new/endpoint/'
    QueryModel = rg_schemas.MyNewRequest
    ResultModel = rg_schemas.MyNewResponse
```

## Health Check Endpoints

The AI Service provides several health check endpoints to verify connectivity to external dependencies. These endpoints are defined in `src/core/health_checks.py` and are registered in `src/main.py`.

### Basic Health Check

- **Endpoint**: `/health-check`
- **Description**: A basic health check that returns a simple status message.
- **Response**: `{"status": "ok"}`

### External Dependency Health Checks

The following endpoints check connectivity to specific external dependencies:

#### OpenAI

- **Endpoint**: `/health-check/openai/check-connection`
- **Description**: Verifies connectivity to OpenAI by making a simple API call.
- **Response**: `{"message": "OpenAI connection successful"}` or an error message.

#### Smith (LangChain Hub)

- **Endpoint**: `/health-check/smith/check-connection`
- **Description**: Verifies connectivity to Smith (LangChain Hub) by pulling a template.
- **Response**: `{"message": "Smith connection successful"}` or an error message.

#### Redis

- **Endpoint**: `/health-check/redis/check-connection`
- **Description**: Verifies connectivity to Redis by pinging the server.
- **Response**: `{"message": "Redis connection successful"}` or an error message.

#### Sentry

- **Endpoint**: `/health-check/sentry/check-connection`
- **Description**: Verifies that Sentry is properly configured.
- **Response**: `{"message": "Sentry connection successful"}` or an error message.

#### OpenMeter

- **Endpoint**: `/health-check/openmeter/check-connection`
- **Description**: Verifies connectivity to OpenMeter by making a simple API call.
- **Response**: `{"message": "OpenMeter connection successful"}` or an error message.

### Circuit Breaker Pattern

All health check endpoints use the circuit breaker pattern to handle service outages gracefully. If a service is unavailable, the circuit breaker will prevent repeated failed calls to the service, reducing the load on the service and improving the responsiveness of the application.

## Conclusion

The AI Service project uses a flexible and extensible architecture for defining, discovering, and registering services and routes. This approach makes it easy to add new functionality to the API without modifying the core routing logic.
