from app.services.base_service import BaseAIServiceWithPrompt
from app.risk.schemas import (
    RiskDefinitionCheckRequest,
    RiskDefinitionCheckResponse,
    RiskIdentificationQuery,
    RiskIdentificationResult,
)


class RiskDefinitionService(BaseAIServiceWithPrompt):
    prompt_name = 'risk-definition-check'
    QueryModel = RiskDefinitionCheckRequest
    ResultModel = RiskDefinitionCheckResponse


class RiskIdentificationService(BaseAIServiceWithPrompt):
    prompt_name_category = 'identify-risk-for-category'
    prompt_name_categories = 'identify-risk-for-categories'
    QueryModel = RiskIdentificationQuery
    ResultModel = RiskIdentificationResult

    def get_prompt_name(self, query: RiskIdentificationQuery = None) -> str:
        """ Custom prompt name selection based on the query details. """
        if query and query.subcategory:
            return self.prompt_name_categories
        return self.prompt_name_category