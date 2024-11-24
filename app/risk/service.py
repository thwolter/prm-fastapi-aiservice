from app.core.ai_service import AIService
from app.risk.schemas import (RiskDefinitionCheckRequest,
                              RiskDefinitionCheckResponse,
                              RiskIdentificationRequest,
                              RiskIdentificationResponse)


class RiskDefinitionService(AIService):
    prompt_name = 'risk-definition-check'
    QueryModel = RiskDefinitionCheckRequest
    ResultModel = RiskDefinitionCheckResponse


class RiskIdentificationService(AIService):
    prompt_name = 'identify-risk-for-category'
    QueryModel = RiskIdentificationRequest
    ResultModel = RiskIdentificationResponse
