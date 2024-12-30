from app.category.schemas import Category
from app.project.schemas import BaseProjectRequest
from pydantic import BaseModel, Field

from app.utils.schema import BaseResponseModel


class Risk(BaseModel):
    title: str = Field(..., description='The title of the risk.')
    description: str = Field(..., description='The description of the risk.')


class RiskDefinitionCheckRequest(BaseModel):
    text: str = Field(..., description='The text to be assessed.')


class RiskDefinitionCheckResponse(BaseResponseModel):
    is_valid: bool = Field(..., description='Whether the text is valid or not.')
    classification: str = Field(..., description='The classification of the text.')
    original: str = Field(..., description='The original text.')
    suggestion: str = Field(..., description='Suggestions for a revised risk definition.')
    explanation: str = Field(..., description='Explanation of the classification.')


class RiskIdentificationRequest(BaseProjectRequest):
    category: Category = Field(..., description='The category of the risks to be identified.')
    existing: list[Risk] = Field([], description='The existing risks.')


class RiskIdentificationResponse(BaseResponseModel):
    risks: list[Risk] = Field(..., description='The list of risks identified.')


class RiskDriversRequest(BaseProjectRequest):
    risk: Risk = Field(..., description='The risk to be assessed.')


class RiskDriversResponse(BaseResponseModel):
    drivers: list[str] = Field(..., description='The drivers of the risk.')
    explanation: str = Field(..., description='Explanation of the drivers classification.')
    sources: list[str] = Field(..., description='The sources of the drivers classification.')


class RiskLikelihoodRequest(BaseProjectRequest):
    risk: Risk = Field(..., description='The risk to be assessed.')


class RiskLikelihoodResponse(BaseResponseModel):
    likelihood: str = Field(..., description='The likelihood of the risk: low, medium, high.')
    explanation: str = Field(..., description='Explanation of the likelihood classification.')
    sources: list[str] = Field(..., description='The sources of the likelihood classification.')


class RiskImpactRequest(BaseProjectRequest):
    risk: Risk = Field(..., description='The risk to be assessed.')


class RiskImpactResponse(BaseResponseModel):
    impacts: list[str] = Field(..., description='The impacts of the risk.')
    level: str = Field(..., description='The level of the impact: low, medium, high.')
    explanation: str = Field(..., description='Explanation of the impact classification.')
    sources: list[str] = Field(..., description='The sources of the impact classification.')


class RiskMitigationRequest(BaseProjectRequest):
    risk: Risk = Field(..., description='The risk to be assessed.')
    drivers: list[str] = Field(..., description='The drivers of the risk.')


class RiskMitigationResponse(BaseResponseModel):
    mitigation: str = Field(..., description='The mitigation of the risk.')
    explanation: str = Field(..., description='Explanation of the mitigation classification.')
    sources: list[str] = Field(..., description='The sources of the mitigation classification.')
