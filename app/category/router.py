import logging
from fastapi import APIRouter

from app.category.schemas import (
    CategoriesIdentificationResponse,
    BaseProjectRequest,
    CategoryAddRequest
)
from app.core.registrar import RouteRegistrar
from app.category.service import (
    CategoryIdentificationService,
    CategoryAddService
)


# Create APIRouter instance
router = APIRouter(
    prefix='/api/categories',
    tags=['Category'],
    responses={404: {'description': 'Not found'}},
)

# Create route registrar
registrar = RouteRegistrar(router)

registrar.register_route(
    '/create/',
    request_model=BaseProjectRequest,
    response_model=CategoriesIdentificationResponse,
    service_class=CategoryIdentificationService
)

registrar.register_route(
    '/add/',
    request_model=CategoryAddRequest,
    response_model=CategoriesIdentificationResponse,
    service_class=CategoryAddService
)
