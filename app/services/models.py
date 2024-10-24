from pydantic import BaseModel, Field


class RiskDefinitionCheckResponse(BaseModel):
    is_valid: bool = Field(..., description='Whether the text is valid or not.')
    classification: str = Field(..., description='The classification of the text.')
    original: str = Field(..., description='The original text.')
    suggestion: str = Field(..., description='Suggestions for a revised risk definition.')
    explanation: str = Field(..., description='Explanation of the classification.')


class RiskDefinitionCheckRequest(BaseModel):
    text: str = Field(..., description='The text to be assessed.')


class RiskIdentificationQuery(BaseModel):
    category: str = Field(..., description='The category of the risk.')
    subcategory: str | None = Field(None, description='The subcategory of the risk.')
    context: str = Field(..., description='The context of the risk.')


class Risk(BaseModel):
    title: str = Field(..., description='The title of the risk.')
    description: str = Field(..., description='The description of the risk.')


class RiskIdentificationResult(BaseModel):
    risks: list[Risk] = Field(..., description='The list of risks identified.')


class Category(BaseModel):
    name: str = Field(..., description='The name of the category.')
    description: str = Field(..., description='The description of the category.')
    examples: list[str] = Field(..., description='Examples of the category.')


class CategoriesIdentificationRequest(BaseModel):
    text: str = Field(..., description='The text to be used for category identification.')


class CategoriesIdentificationResponse(BaseModel):
    categories: list[Category] = Field(..., description='The list of categories identified.')


class CheckProjectContextRequest(BaseModel):
    project_name: str = Field(..., description='The name of the project.')
    project_context: str = Field(..., description='The project context to be checked.')


class CheckProjectContextResponse(BaseModel):
    is_valid: bool = Field(..., description='Whether the project context is valid or not.')
    suggestion: str = Field(..., description='Suggestions for a revised project context.')
    explanation: str = Field(..., description='Explanation of the classification.')
    missing: list[str] = Field(..., description='The list of missing elements in the project context.')
