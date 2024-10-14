from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from app.service import RiskDefinitionService

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

class RiskDescriptionRequest(BaseModel):
    text: str

class RiskDescriptionResponse(BaseModel):
    is_valid: bool
    classification: str
    original: str
    suggestions: str

service = RiskDefinitionService()

@router.post('/check/risk-definition/')
def check_risk_definition(request: RiskDescriptionRequest) -> RiskDescriptionResponse:
    try:
        result = service.assess_text(request.text)
        return RiskDescriptionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
