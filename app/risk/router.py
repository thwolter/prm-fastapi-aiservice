import logging
from fastapi import APIRouter

from app.risk.schemas import (
    RiskDefinitionCheckRequest,
    RiskDefinitionCheckResponse,
)
from app.core.registrar import RouteRegistrar
from app.risk.service import (
    RiskDefinitionService,
)

# Create APIRouter instance
router = APIRouter(
    prefix='/api/risk',
    tags=['Risk'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)

# Register all routes with simplified code
registrar.register_route(
    '/check/definition/',
    request_model=RiskDefinitionCheckRequest,
    response_model=RiskDefinitionCheckResponse,
    service_class=RiskDefinitionService
)
