import re

from fastapi import Request
from starlette.types import ASGIApp

from src.utils import logutils

logger = logutils.get_logger(__name__)


class MiddlewareSkipMixin:
    """
    Mixin class that provides functionality to determine if middleware processing
    should be skipped for certain paths.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

        # Define paths and patterns to exclude
        self.excluded_paths = {
            # Documentation routes
            "/docs",
            "/redoc",
            "/openapi.json",
            # Root health check
            "/api/_health",
        }

        # Define path patterns to exclude (using regex)
        self.excluded_patterns = [
            # Health check routes
            r"^/health-check.*",
            # Static files
            r"^/static/.*",
        ]

        logger.info(f"TokenEntitlementMiddleware will exclude paths: {self.excluded_paths}")
        logger.info(f"TokenEntitlementMiddleware will exclude patterns: {self.excluded_patterns}")

    def should_skip_middleware(self, request: Request) -> bool:
        """
        Determine if the middleware should be skipped for this path.

        Args:
            path: The request path

        Returns:
            bool: True if the middleware should be skipped, False otherwise
        """

        path = request.url.path

        # Check if path is in excluded paths
        if path in self.excluded_paths:
            logger.debug(f"Skipping middleware for excluded path: {path}")
            return True

        # Check if path matches any excluded pattern
        for pattern in self.excluded_patterns:
            if re.match(pattern, path):
                logger.debug(f"Skipping middleware for excluded pattern match: {path}")
                return True

        # Check if this is a service route we should process
        if hasattr(self, "service_routes") and self.service_routes:
            is_service_route = False
            for route in self.service_routes:
                # Handle both exact matches and routes with API prefix
                if path.endswith(route) or path == route:
                    is_service_route = True
                    break

            # Skip if not a service route
            if not is_service_route:
                logger.debug(f"Skipping middleware for non-service path: {path}")
                return True

        return False
