from app.core.ai_service import AIService
from app.risk.schemas import (RiskDefinitionCheckRequest,
                              RiskDefinitionCheckResponse,
                              RiskIdentificationRequest,
                              RiskIdentificationResponse)


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

