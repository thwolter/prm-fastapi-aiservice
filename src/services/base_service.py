"""Base service for RiskGPT operations."""
from __future__ import annotations

import logging
from typing import Type

from pydantic import BaseModel

from src.utils.resilient import with_resilient_execution

# Configure logger
logger = logging.getLogger(__name__)

class BaseService:
    """Base service calling RiskGPT chains."""

    chain_fn: callable
    route_path: str
    QueryModel: Type[BaseModel]
    ResultModel: Type[BaseModel]

    async def execute_query(self, query: BaseModel):
        """Execute a query using the chain function with resilient execution.

        Args:
            query: The query to execute.

        Returns:
            The result of the query.

        Raises:
            RuntimeError: If riskgpt is not installed.
            ExternalServiceException: If the service is unavailable and no fallback is provided.
        """
        if not self.chain_fn:
            raise RuntimeError('riskgpt is not installed')

        # Use the resilient execution decorator to handle fallbacks and circuit breaking
        return await self._execute_with_resilience(query)

    def _create_default_response(self, query: BaseModel):
        """Create a default response when the service is unavailable.

        Args:
            query: The original query.

        Returns:
            A default response of the appropriate ResultModel type.
        """
        return self.ResultModel(
            success=False,
            error=f"Service {self.__class__.__name__} is temporarily unavailable"
        )

    @with_resilient_execution(
        service_name=lambda self, query: self.__class__.__name__,
        create_default_response=lambda self, query: self._create_default_response(query)
    )
    async def _execute_with_resilience(self, query: BaseModel):
        """Execute the query with resilient execution.

        This method is decorated with with_resilient_execution to provide
        circuit breaker and fallback functionality.

        Args:
            query: The query to execute.

        Returns:
            The result of the chain function.
        """
        return await self.chain_fn(query)
