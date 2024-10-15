import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_risk_definition_service
from app.models import (RiskDefinitionCheckQuery, RiskDefinitionCheckRequest,
                        RiskDefinitionCheckResponse)
from app.services.services import RiskDefinitionService

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@router.post('/risk-definition/check/', response_model=RiskDefinitionCheckResponse)
def check_risk_definition(
    request: RiskDefinitionCheckRequest,
    service: RiskDefinitionService = Depends(get_risk_definition_service)
) -> RiskDefinitionCheckResponse:
    try:
        result = service.execute_query(RiskDefinitionCheckQuery(text=request.text))
        return RiskDefinitionCheckResponse(**result.model_dump())
    except Exception as e:
        logging.error(f"Error in check_risk_definition: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")