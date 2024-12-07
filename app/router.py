from fastapi import APIRouter
from app.core.registrar import RouteRegistrar
from app.risk.service import RiskDefinitionService, RiskIdentificationService, RiskDriverService, RiskLikelihoodService, \
    RiskImpactService, RiskMitigationService
from app.project.service import CheckProjectContextService, ProjectSummaryService
from app.category.service import CategoryIdentificationService, CategoryAddService

services = [
    CheckProjectContextService,
    ProjectSummaryService,
    RiskDefinitionService,
    RiskIdentificationService,
    RiskDriverService,
    RiskLikelihoodService,
    RiskImpactService,
    RiskMitigationService,
    CategoryIdentificationService,
    CategoryAddService
]

router = APIRouter(
    prefix='/api',
    responses={404: {'description': 'Not found'}},
)

registrar = RouteRegistrar(router)

for service_class in services:
    registrar.register_route(
        path=service_class.route_path,  # Use route path defined in the service
        request_model=service_class.QueryModel,
        response_model=service_class.ResultModel,
        service_factory=lambda cls=service_class: cls(),  # Dynamically instantiate
    )