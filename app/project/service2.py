import hashlib

from core.ai_service import BaseLLMService
from project.schemas import Project, ProjectSummaryResponse, BaseProjectRequest
from langchain_core.output_parsers import PydanticOutputParser


class ProjectService(BaseLLMService):

    def __init__(self, project: Project):
        super().__init__()
        self.project = project


    def model_hash(self):
        project_json = self.project.model_dump_json().encode('utf-8')
        hash_object = hashlib.md5(project_json)
        return hash_object.hexdigest()


    async def get_project_summary(self) -> ProjectSummaryResponse:
        parser = PydanticOutputParser(pydantic_object=ProjectSummaryResponse)
        return await self.execute_query('summarize-project', self.project, parser)