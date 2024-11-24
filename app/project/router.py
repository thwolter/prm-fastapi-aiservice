import logging
from fastapi import APIRouter

from app.project.schemas import (
    BaseProjectRequest,
    CheckProjectContextResponse,
    ProjectSummaryResponse
)
from app.services.router import RouteRegistrar
from app.project.service import CheckProjectContextService, ProjectSummaryService


# Create APIRouter instance
router = APIRouter(
    prefix='/api/project',
    tags=['Project'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)

registrar.register_route(
    '/check/context/',
    request_model=BaseProjectRequest,
    response_model=CheckProjectContextResponse,
    service_class=CheckProjectContextService
)

registrar.register_route(
    '/summarize/',
    request_model=BaseProjectRequest,
    response_model=ProjectSummaryResponse,
    service_class=ProjectSummaryService
)