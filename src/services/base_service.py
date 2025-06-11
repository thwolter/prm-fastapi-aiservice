"""Base service for RiskGPT operations."""
from __future__ import annotations

import logging
from typing import Type

from pydantic import BaseModel
from pydantic.fields import PydanticUndefined

try:  # pragma: no cover - riskgpt optional dependency
    from riskgpt.models.schemas import ResponseInfo
except Exception:  # pragma: no cover - fallback for tests without riskgpt
    class ResponseInfo(BaseModel):
        consumed_tokens: int
        total_cost: float
        prompt_name: str
        model_name: str
        error: str | None = None

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
        """Create a default ``ResultModel`` instance for fallback scenarios.

        The newer ``riskgpt`` response models do not provide ``success`` or
        ``error`` fields. Instead, they expose an optional ``response_info``
        object which itself contains an ``error`` attribute. When a service
        fails we still need to return a valid instance of the expected
        ``ResultModel``. This helper builds such an instance by populating all
        required fields with sensible default values and attaching the error
        information to ``response_info``.
        """
        from typing import get_args, get_origin

        def default_for_annotation(annotation):
            origin = get_origin(annotation)
            if origin is list:
                return []
            if origin is dict:
                return {}
            if origin is not None and origin is not list and origin is not dict:
                args = [a for a in get_args(annotation) if a is not type(None)]
                return default_for_annotation(args[0]) if args else None
            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                values = {
                    name: (
                        field.default
                        if field.default is not None
                        else default_for_annotation(field.annotation)
                    )
                    for name, field in annotation.model_fields.items()
                }
                return annotation(**values)
            if annotation is str:
                return ""
            if annotation is bool:
                return False
            if annotation is int:
                return 0
            if annotation is float:
                return 0.0
            return None

        values = {}
        for name, field in self.ResultModel.model_fields.items():
            if name == "response_info":
                continue
            if field.default is not PydanticUndefined:
                values[name] = field.default
            else:
                values[name] = default_for_annotation(field.annotation)

        from src.utils.circuit_breaker import get_circuit_breaker

        circuit = get_circuit_breaker(self.__class__.__name__)
        if not circuit.allow_request():
            error_msg = f"Service {self.__class__.__name__} is currently unavailable"
        else:
            error_msg = f"Service {self.__class__.__name__} is temporarily unavailable"

        if "response_info" in self.ResultModel.model_fields:
            values["response_info"] = ResponseInfo(
                consumed_tokens=0,
                total_cost=0.0,
                prompt_name="",
                model_name="",
                error=error_msg,
            )

        if "error" in self.ResultModel.model_fields:
            values["error"] = error_msg

        return self.ResultModel(**values)

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
        return await self.__class__.chain_fn(query)
