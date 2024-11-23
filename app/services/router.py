import logging
from typing import Type, TypeVar, Generic, Callable
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.models import (
    CategoriesIdentificationResponse,
    BaseProjectRequest,
    CheckProjectContextResponse,
    RiskDefinitionCheckRequest,
    RiskDefinitionCheckResponse, ProjectSummaryResponse, CategoryAddRequest, CategoryAddResponse
)
from app.services.services import (
    CategoryIdentificationService,
    CheckProjectContextService,
    RiskDefinitionService, ProjectSummaryService, CategoryAddService
)

TRequest = TypeVar('TRequest', bound=BaseModel)
TResponse = TypeVar('TResponse', bound=BaseModel)


class BaseServiceHandler(Generic[TRequest, TResponse]):
    def __init__(self, service_class: Type, request_model: Type[TRequest], response_model: Type[TResponse]):
        self.service_class = service_class
        self.request_model = request_model
        self.response_model = response_model

    def handle(self, request: TRequest) -> TResponse:
        service = self.service_class()
        try:
            query = self.request_model(**request.model_dump())
            result = service.execute_query(query)
            return self.response_model(**result.model_dump())
        except Exception as e:
            logging.error(f'Error in {self.service_class.__name__}: {e}')
            raise HTTPException(status_code=500, detail='Internal Server Error')


class RouteRegistrar:
    def __init__(self, api_router: APIRouter):
        self.router = api_router

    def register_route(
        self,
        path: str,
        request_model: Type[TRequest],
        response_model: Type[TResponse],
        service_class: Type,
    ):
        handler = BaseServiceHandler(service_class, request_model, response_model)

        def route_function(request: request_model) -> response_model:
            return handler.handle(request)

        self.router.post(path, response_model=response_model)(route_function)


# Create APIRouter instance
router = APIRouter(
    prefix='/api',
    tags=['api'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)

# Register all routes with simplified code
registrar.register_route(
    '/risk-definition/check/',
    RiskDefinitionCheckRequest,
    RiskDefinitionCheckResponse,
    RiskDefinitionService
)

registrar.register_route(
    '/categories/create/',
    BaseProjectRequest,
    CategoriesIdentificationResponse,
    CategoryIdentificationService
)

registrar.register_route(
    '/categories/add/',
    CategoryAddRequest,
    CategoriesIdentificationResponse,
    CategoryAddService
)

registrar.register_route(
    '/project/check/context/',
    BaseProjectRequest,
    CheckProjectContextResponse,
    CheckProjectContextService
)

registrar.register_route(
    '/project/summarize/',
    BaseProjectRequest,
    ProjectSummaryResponse,
    ProjectSummaryService
)