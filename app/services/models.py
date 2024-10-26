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


class IdentifiedCategory(Category):
    confidence: float = Field(..., description='The confidence score of the identification.')
    subcategories: list['IdentifiedCategory'] = Field(default_factory=list, description='List of subcategories.')


class CategoriesIdentificationResponse(BaseModel):
    risks: list[IdentifiedCategory] = Field(..., description='The list of identified risk categories.')
    opportunities: list[IdentifiedCategory] = Field(..., description='The list of identified opportunity categories.')
    impact: list[IdentifiedCategory] = Field(..., description='The list of identified impact categories.')


class BaseProjectRequest(BaseModel):
    name: str = Field(..., description='The name of the project.')
    context: str = Field(..., description='The project context to be checked.')


class CheckProjectContextResponse(BaseModel):
    is_valid: bool = Field(..., description='Whether the project context is valid or not.')
    suggestion: str = Field(..., description='Suggestions for a revised project context.')
    explanation: str = Field(..., description='Explanation of the classification.')
    missing: list[str] = Field(..., description='The list of missing elements in the project context.')
    context_example: str = Field(..., description='An example of a valid project context.')
    language: str = Field(..., description='The language of the project context.')
    capabilities: list[str] = Field(..., description='The list of capabilities required for the project.')
    challenges: list[str] = Field(..., description='The list of challenges faced by the project.')
    budget: str = Field(..., description='The budget of the project.')
    timeline: str = Field(..., description='The timeline of the project.')


class ProjectSummaryResponse(BaseModel):
    summary: str = Field(..., description='A summary of the project.')
    image_url: str = Field(..., description='URL for the project picture.')
    tags: list[str] = Field(..., description='Tags associated with the project.')