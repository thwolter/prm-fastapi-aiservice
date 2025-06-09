"""Base service for RiskGPT operations."""
from __future__ import annotations

from typing import Type

from pydantic import BaseModel

class RiskGPTService:
    """Base service calling RiskGPT chains."""

    chain_fn: callable
    route_path: str
    QueryModel: Type[BaseModel]
    ResultModel: Type[BaseModel]
    prompt_name: str = None  # Optional attribute for category services

    async def execute_query(self, query: BaseModel):
        """Execute a query using the chain function.

        Args:
            query: The query to execute.

        Returns:
            The result of the query.

        Raises:
            RuntimeError: If riskgpt is not installed.
        """
        if not self.chain_fn:
            raise RuntimeError('riskgpt is not installed')
        return await self.chain_fn(query)