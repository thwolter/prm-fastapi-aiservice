"""
Route-related functionality for the AI Service.

This package contains modules for handling route registration, service handling,
and request/response validation.
"""

# Re-export key classes and functions for backward compatibility
from routes.route_registry import RouteRegistry
from routes.router_factory import create_router
from routes.service_handler import ServiceHandler
from routes.validation import validate_model