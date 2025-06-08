from typing import List, Optional
from pydantic import BaseModel, Field

from src.utils.schema import BaseResponseModel
from src.project.schemas import Project
from src.category.schemas import Category


class Risk(BaseModel):
    """Simple risk representation used in tests."""

    title: str = Field(..., description='Risk title')
    description: str = Field(..., description='Risk description')


class RiskDefinitionCheckResponse(BaseResponseModel):
    is_valid: bool
    classification: str
    original: str
    suggestion: str
    explanation: str


class RiskIdentificationRequest(BaseModel):
    project: Project
    category: Category
    risks: Optional[List[Risk]] = None
    existing: Optional[List[Risk]] = None


class RiskIdentificationResponse(BaseResponseModel):
    risks: List[Risk]


class RiskDriversRequest(BaseModel):
    name: str
    context: str
    risk: Risk


class RiskDriversResponse(BaseResponseModel):
    drivers: List[str]


class RiskLikelihoodResponse(BaseResponseModel):
    probability: Optional[float] = None


class RiskImpactResponse(BaseResponseModel):
    impact: Optional[float] = None


class RiskMitigationResponse(BaseResponseModel):
    mitigations: List[str]


__all__ = [
    'Risk',
    'RiskDefinitionCheckResponse',
    'RiskIdentificationRequest',
    'RiskIdentificationResponse',
    'RiskDriversRequest',
    'RiskDriversResponse',
    'RiskLikelihoodResponse',
    'RiskImpactResponse',
    'RiskMitigationResponse',
]
