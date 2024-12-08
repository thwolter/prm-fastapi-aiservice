from pydantic import BaseModel, Field

from app.project.schemas import BaseProjectRequest


class Category(BaseModel):
    name: str = Field(..., description='The name of the category.')
    description: str = Field(..., description='The description of the category.')
    examples: list[str] = Field(..., description='Examples of the category.')


class CategoriesIdentificationRequest(BaseModel):
    name: str = Field(..., description='The name of the project.')
    context: str = Field(..., description='The context of the project.')


class IdentifiedCategory(Category):
    confidence: float = Field(..., description='The confidence score of the identification.')
    subcategories: list['IdentifiedCategory'] = Field(
        default_factory=list, description='List of subcategories.'
    )


class CategoriesIdentificationResponse(BaseModel):
    risks: list[IdentifiedCategory] = Field(
        ..., description='The list of identified risk categories.'
    )
    opportunities: list[IdentifiedCategory] = Field(
        ..., description='The list of identified opportunity categories.'
    )
    impact: list[IdentifiedCategory] = Field(
        ..., description='The list of identified impact categories.'
    )


class CategoryAddRequest(BaseProjectRequest):
    type: str = Field(..., description='The type of category to be added.')
    existing: list[Category] = Field(
        ..., description='Existing categories which must be excluded from the identification.'
    )


class CategoryAddResponse(BaseModel):
    categories: list[IdentifiedCategory] = Field(
        ..., description='The list of identified categories.'
    )
