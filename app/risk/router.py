from fastapi import APIRouter

from app.core.registrar import RouteRegistrar
from app.risk.schemas import (RiskDefinitionCheckRequest,
                              RiskDefinitionCheckResponse,
                              RiskIdentificationRequest,
                              RiskIdentificationResponse)
from app.risk.service import RiskDefinitionService, RiskIdentificationService

router = APIRouter(
    prefix='/api/risk',
    tags=['Risk'],
    responses={404: {'description': 'Not found'}},
)

registrar = RouteRegistrar(router)

registrar.register_route(
    '/check/definition/',
    request_model=RiskDefinitionCheckRequest,
    response_model=RiskDefinitionCheckResponse,
    service_factory=lambda: RiskDefinitionService(),
)

registrar.register_route(
    '/identify/',
    request_model=RiskIdentificationRequest,
    response_model=RiskIdentificationResponse,
    service_factory=lambda: RiskIdentificationService(),
)
