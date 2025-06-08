from src.core.ai_service import AIService
from src.risk.service import RiskGPTService
from riskgpt import chains

from src.context.schemas import (
    BaseProjectRequest,
    CheckProjectContextResponse,
    ContextQualityRequest,
    ContextQualityResponse,
    ProjectSummaryResponse,
)


class CheckProjectContextService(AIService):
    prompt_name = 'check-project-context'
    route_path = '/project/check/context/'
    QueryModel = BaseProjectRequest
    ResultModel = CheckProjectContextResponse


class ProjectSummaryService(AIService):
    prompt_name = 'summarize-project'
    route_path = '/project/summarize/'
    QueryModel = BaseProjectRequest
    ResultModel = ProjectSummaryResponse


class ContextQualityService(RiskGPTService):
    """Service wrapper for the RiskGPT context quality chain."""

    try:  # pragma: no cover - optional dependency
        chain_fn = chains.async_get_context_quality_chain
    except AttributeError:  # pragma: no cover - missing chain
        async def chain_fn(query):  # type: ignore[override]
            raise NotImplementedError('Context quality chain not available')

    route_path = '/context/check/'
    QueryModel = ContextQualityRequest
    ResultModel = ContextQualityResponse
