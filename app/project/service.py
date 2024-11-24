from app.project.schemas import CheckProjectContextResponse, BaseProjectRequest, ProjectSummaryResponse
from app.services.base_service import BaseAIServiceWithPrompt


class CheckProjectContextService(BaseAIServiceWithPrompt):
    prompt_name = 'check-project-context'
    QueryModel = BaseProjectRequest
    ResultModel = CheckProjectContextResponse


class ProjectSummaryService(BaseAIServiceWithPrompt):
    prompt_name = 'summarize-project'
    QueryModel = BaseProjectRequest
    ResultModel = ProjectSummaryResponseel = ProjectSummaryResponse