from app.services.base_service import BaseAIServiceWithPrompt
from app.services.models import (
    CategoriesIdentificationRequest,
    CategoriesIdentificationResponse,
    BaseProjectRequest,
    CheckProjectContextResponse,
    RiskDefinitionCheckRequest,
    RiskDefinitionCheckResponse,
    RiskIdentificationQuery,
    RiskIdentificationResult,
    ProjectSummaryResponse
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


class CategoryIdentificationService(BaseAIServiceWithPrompt):
    prompt_name = 'create-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse


class CategoryAddService(BaseAIServiceWithPrompt):
    prompt_name = 'add-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse
