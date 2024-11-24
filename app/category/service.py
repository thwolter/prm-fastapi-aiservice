from app.category.schemas import (CategoriesIdentificationRequest,
                                  CategoriesIdentificationResponse)
from app.core.ai_service import AIService


class CategoryIdentificationService(AIService):
    prompt_name = 'create-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse


class CategoryAddService(AIService):
    prompt_name = 'add-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse
