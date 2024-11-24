from project.schemas import BaseProjectRequest
from pydantic import BaseModel, Field


class Risk(BaseModel):
    title: str = Field(..., description='The title of the risk.')
    description: str = Field(..., description='The description of the risk.')


class RiskDefinitionCheckRequest(BaseModel):
    text: str = Field(..., description='The text to be assessed.')


class RiskDefinitionCheckResponse(BaseModel):
    is_valid: bool = Field(..., description='Whether the text is valid or not.')
    classification: str = Field(..., description='The classification of the text.')
    original: str = Field(..., description='The original text.')
    suggestion: str = Field(..., description='Suggestions for a revised risk definition.')
    explanation: str = Field(..., description='Explanation of the classification.')


class RiskIdentificationRequest(BaseProjectRequest):
    category: str = Field(..., description='The category of the risk.')
    existing: list[Risk] = Field([], description='The existing risks.')


class RiskIdentificationResponse(BaseModel):
    risks: list[Risk] = Field(..., description='The list of risks identified.')
