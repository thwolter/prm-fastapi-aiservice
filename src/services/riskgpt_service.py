from __future__ import annotations

from typing import Type

from pydantic import BaseModel

try:  # pragma: no cover - optional dependency
    from riskgpt import chains
    from riskgpt.models.schemas import CategoryRequest, CategoryResponse
except Exception:  # pragma: no cover - riskgpt not installed
    chains = None

    class CategoryRequest(BaseModel):
        """Fallback request schema when riskgpt is unavailable."""

        project_id: str
        project_description: str
        domain_knowledge: str | None = None
        language: str | None = "en"

    class CategoryResponse(BaseModel):
        """Fallback response schema when riskgpt is unavailable."""

        categories: list[str]
        rationale: str | None = None
        response_info: dict | None = None


class RiskGPTCategoryService:
    """Service wrapping RiskGPT category chain."""

    chain_fn = chains.async_get_categories_chain if chains else None
    route_path = '/categories/'
    QueryModel: Type[BaseModel] = CategoryRequest
    ResultModel: Type[BaseModel] = CategoryResponse

    async def execute_query(self, query: BaseModel):
        if not self.chain_fn:
            raise RuntimeError('riskgpt is not installed')
        return await self.chain_fn(query)
