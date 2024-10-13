from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

@router.post('/check/risk-definition/')
def check_risk_definition():
    return {'result': 'ok'}

