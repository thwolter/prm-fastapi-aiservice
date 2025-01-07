
import httpx
from fastapi import HTTPException, Request
from uuid import UUID

from core.config import settings
from project.schemas import Project
from project.service2 import ProjectService


async def get_project_service(project_id: UUID, request: Request) -> ProjectService:
    project = await get_project(project_id, request)
    return ProjectService(project)


async def get_project(project_id: UUID, request: Request) -> Project:
    auth_token = request.state.token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{settings.DATASERVICE_URL}/projects/{project_id}/',
            headers={'Cookie': f'auth={auth_token}'},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    return Project.model_validate(response.json())

