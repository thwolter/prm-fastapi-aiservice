from app.models import (RiskDefinitionCheckQuery, RiskDefinitionCheckResult,
                        RiskIdentificationQuery, RiskIdentificationResult, CategoriesIdentificationRequest,
                        CategoriesIdentificationResponse)
from app.services.base_service import BaseAIService


class RiskDefinitionService(BaseAIService):
    prompt_name = "risk-definition-check"
    QueryModel = RiskDefinitionCheckQuery
    ResultModel = RiskDefinitionCheckResult


class RiskIdentificationService(BaseAIService):
    prompt_name_category = "identify-risk-for-category"
    prompt_name_categories = "identify-risk-for-categories"
    QueryModel = RiskIdentificationQuery
    ResultModel = RiskIdentificationResult

    def get_prompt_name(self, query: RiskIdentificationQuery) -> str:
        if query.subcategory:
            return self.prompt_name_categories
        return self.prompt_name_category


class CategoryIdentificationService(BaseAIService):
    prompt_name = "create-categories"
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse