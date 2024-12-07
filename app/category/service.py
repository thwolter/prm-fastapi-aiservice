from app.category.schemas import (CategoriesIdentificationRequest,
                                  CategoriesIdentificationResponse)
from app.core.ai_service import AIService


class CategoryIdentificationService(AIService):
    prompt_name = 'create-categories'
    route_path = '/categories/create/'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse


class CategoryAddService(AIService):
    prompt_name = 'add-categories'
    route_path = '/categories/add/'
    QueryModel = CategoriesIdentificationRequest
    ResultModel = CategoriesIdentificationResponse
