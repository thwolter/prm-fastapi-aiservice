import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.models import (RiskDefinitionCheckQuery, RiskDefinitionCheckRequest,
                        RiskDefinitionCheckResponse, CategoriesIdentificationRequest,
                        CategoriesIdentificationResponse)
from app.services.services import RiskDefinitionService, CategoryIdentificationService

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@router.post('/risk-definition/check/', response_model=RiskDefinitionCheckResponse)
def check_risk_definition(request: RiskDefinitionCheckRequest) -> RiskDefinitionCheckResponse:
    service = RiskDefinitionService()
    try:
        result = service.execute_query(RiskDefinitionCheckQuery(text=request.text))
        return RiskDefinitionCheckResponse(**result.model_dump())
    except Exception as e:
        logging.error(f"Error in check_risk_definition: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/categories/identify/', response_model=CategoriesIdentificationResponse)
def identify_categories(request: CategoriesIdentificationRequest) -> CategoriesIdentificationResponse:
    service = CategoryIdentificationService()
    try:
        result = service.execute_query(request)
        return CategoriesIdentificationResponse(**result.model_dump())
    except Exception as e:
        logging.error(f"Error in identify_categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")