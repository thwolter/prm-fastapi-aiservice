from src.core.ai_service import AIService
from src.project.schemas import (BaseProjectRequest,
                                 CheckProjectContextResponse,
                                 ProjectSummaryResponse)


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
