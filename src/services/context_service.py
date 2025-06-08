from pydantic import BaseModel

from src.core.ai_service import AIService


class ContextRequest(BaseModel):
    text: str


class ContextResponse(BaseModel):
    reversed: str


class ContextService(AIService):
    """Simple service used for testing service discovery."""

    prompt_name = 'context-test'
    route_path = '/context/test/'
    QueryModel = ContextRequest
    ResultModel = ContextResponse

    async def execute_query(self, query: ContextRequest) -> ContextResponse:
        return ContextResponse(reversed=query.text[::-1])
