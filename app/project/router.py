from auth.dependencies import get_current_user
from project.dependencies import get_project, get_project_service
from project.schemas import ProjectSummaryResponse, Project
from fastapi import APIRouter, Depends, Request

from project.service2 import ProjectService

router = APIRouter(
    prefix='/api/project',
    tags=['Project'],
    responses={404: {'description': 'Not found'}},
)

@router.get('/summarize/', response_model=ProjectSummaryResponse, deprecated=True)
async def project_summary(
        service: ProjectService = Depends(get_project_service),
        current_user = Depends(get_current_user)
) -> ProjectSummaryResponse:
    return await service.get_project_summary()