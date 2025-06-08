from src.core.ai_service import AIService
from riskgpt.models.schemas import (
    AssessmentRequest,
    AssessmentResponse,
    DefinitionCheckRequest,
    DefinitionCheckResponse,
    DriverRequest,
    DriverResponse,
    MitigationRequest,
    MitigationResponse,
    RiskRequest,
    RiskResponse,
)


class RiskDefinitionService(AIService):
    prompt_name = 'risk-definition-check'
    route_path = '/risk/check/definition/'
    QueryModel = DefinitionCheckRequest
    ResultModel = DefinitionCheckResponse


class RiskIdentificationService(AIService):
    prompt_name = 'identify-risk-for-category'
    route_path = '/risk/identify/'
    QueryModel = RiskRequest
    ResultModel = RiskResponse


class RiskDriverService(AIService):
    prompt_name = 'risk-drivers'
    route_path = '/risk/drivers/'
    QueryModel = DriverRequest
    ResultModel = DriverResponse


class RiskLikelihoodService(AIService):
    prompt_name = 'risk-likelihood'
    route_path = '/risk/likelihood/'
    QueryModel = AssessmentRequest
    ResultModel = AssessmentResponse


class RiskImpactService(AIService):
    prompt_name = 'risk-impact'
    route_path = '/risk/impact/'
    QueryModel = AssessmentRequest
    ResultModel = AssessmentResponse


class RiskMitigationService(AIService):
    prompt_name = 'risk-mitigation'
    route_path = '/risk/mitigation/'
    QueryModel = MitigationRequest
    ResultModel = MitigationResponse
