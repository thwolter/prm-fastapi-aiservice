from app.core.ai_service import AIService
from app.risk.schemas import (RiskDefinitionCheckRequest,
                              RiskDefinitionCheckResponse, RiskDriversRequest,
                              RiskDriversResponse, RiskIdentificationRequest,
                              RiskIdentificationResponse, RiskImpactRequest,
                              RiskImpactResponse, RiskLikelihoodRequest,
                              RiskLikelihoodResponse, RiskMitigationRequest,
                              RiskMitigationResponse)


class RiskDefinitionService(AIService):
    prompt_name = 'risk-definition-check'
    route_path = '/risk/check/definition/'
    QueryModel = RiskDefinitionCheckRequest
    ResultModel = RiskDefinitionCheckResponse


class RiskIdentificationService(AIService):
    prompt_name = 'identify-risk-for-category'
    route_path = '/risk/identify/'
    QueryModel = RiskIdentificationRequest
    ResultModel = RiskIdentificationResponse


class RiskDriverService(AIService):
    prompt_name = 'risk-drivers'
    route_path = '/risk/drivers/'
    QueryModel = RiskDriversRequest
    ResultModel = RiskDriversResponse


class RiskLikelihoodService(AIService):
    prompt_name = 'risk-likelihood'
    route_path = '/risk/likelihood/'
    QueryModel = RiskLikelihoodRequest
    ResultModel = RiskLikelihoodResponse


class RiskImpactService(AIService):
    prompt_name = 'risk-impact'
    route_path = '/risk/impact/'
    QueryModel = RiskImpactRequest
    ResultModel = RiskImpactResponse


class RiskMitigationService(AIService):
    prompt_name = 'risk-mitigation'
    route_path = '/risk/mitigation/'
    QueryModel = RiskMitigationRequest
    ResultModel = RiskMitigationResponse
