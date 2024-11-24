from app.core.ai_service import BaseAIServiceWithPrompt
from app.category.schemas import (
    CategoriesIdentificationRequest,
    CategoriesIdentificationResponse,
)


class CategoryIdentificationService(BaseAIServiceWithPrompt):
    prompt_name = 'create-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse


class CategoryAddService(BaseAIServiceWithPrompt):
    prompt_name = 'add-categories'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse
