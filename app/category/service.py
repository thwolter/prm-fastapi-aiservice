from app.category.schemas import (AddCategoriesRequest, CategoriesResponse,
                                  CreateCategoriesRequest)
from app.core.ai_service import AIService


class CreateRiskCategoriesService(AIService):
    prompt_name = 'create__project-risks__categories'
    route_path = '/categories/risk/create/'
    QueryModel = CreateCategoriesRequest
    ResultModel = CategoriesResponse


class CreateOpportunitiesCategoriesService(AIService):
    prompt_name = 'create__project-opportunities__categories'
    route_path = '/categories/opportunities/create/'
    QueryModel = CreateCategoriesRequest
    ResultModel = CategoriesResponse


class AddRiskCategoriesService(AIService):
    prompt_name = 'add__project-risks__categories'
    route_path = '/categories/risk/add/'
    QueryModel = AddCategoriesRequest
    ResultModel = CategoriesResponse


class AddOpportunitiesCategoriesService(AIService):
    prompt_name = 'add__project-opportunities__categories'
    route_path = '/categories/opportunities/add/'
    QueryModel = AddCategoriesRequest
    ResultModel = CategoriesResponse
