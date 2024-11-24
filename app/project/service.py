from app.core.ai_service import BaseAIServiceWithPrompt
from app.project.schemas import (BaseProjectRequest,
                                 CheckProjectContextResponse,
                                 ProjectSummaryResponse)


class CheckProjectContextService(BaseAIServiceWithPrompt):
    prompt_name = 'check-project-context'
    QueryModel = BaseProjectRequest
    ResultModel = CheckProjectContextResponse


class ProjectSummaryService(BaseAIServiceWithPrompt):
    prompt_name = 'summarize-project'
    QueryModel = BaseProjectRequest
    ResultModel = ProjectSummaryResponse
