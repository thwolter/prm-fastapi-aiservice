from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.risk_definition_check import (RiskDefinitionCheckQuery,
                                                RiskDefinitionService)

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

#todo: adjust code for routers

class RiskDescriptionRequest(BaseModel):
    text: str

class RiskDescriptionResponse(BaseModel):
    is_valid: bool
    classification: str
    original: str
    suggestions: str

service = RiskDefinitionService()

@router.post('/risk-definition/check/')
def check_risk_definition(request: RiskDescriptionRequest) -> RiskDescriptionResponse:
    try:
        result = service.execute_query(RiskDefinitionCheckQuery(text=request.text))
        return RiskDescriptionResponse(**result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
