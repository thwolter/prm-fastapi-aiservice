import logging
from typing import Type, TypeVar

from fastapi import APIRouter, HTTPException

from app.models import (CategoriesIdentificationRequest,
                        CategoriesIdentificationResponse,
                        RiskDefinitionCheckRequest,
                        RiskDefinitionCheckResponse)
from app.services.services import (CategoryIdentificationService,
                                   RiskDefinitionService)

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


def execute_service_query(
    service_class: Type,
    request: TRequest,
    query_model: Type,
    response_model: Type[TResponse],
) -> TResponse:
    service = service_class()
    try:
        query = query_model(**request.model_dump())
        result = service.execute_query(query)
        return response_model(**result.model_dump())
    except Exception as e:
        logging.error(f"Error in {service_class.__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/risk-definition/check/", response_model=RiskDefinitionCheckResponse)
def check_risk_definition(
    request: RiskDefinitionCheckRequest,
) -> RiskDefinitionCheckResponse:
    return execute_service_query(
        RiskDefinitionService,
        request,
        RiskDefinitionCheckRequest,
        RiskDefinitionCheckResponse,
    )


@router.post("/categories/identify/", response_model=CategoriesIdentificationResponse)
def identify_categories(
    request: CategoriesIdentificationRequest,
) -> CategoriesIdentificationResponse:
    return execute_service_query(
        CategoryIdentificationService,
        request,
        CategoriesIdentificationRequest,
        CategoriesIdentificationResponse,
    )
