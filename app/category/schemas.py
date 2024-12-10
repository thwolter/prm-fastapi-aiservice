from pydantic import BaseModel, Field

from app.project.schemas import BaseProjectRequest


class Category(BaseModel):
    name: str = Field(..., description='The name of the category.')
    description: str = Field(..., description='The description of the category.')


class IdentifiedCategory(Category):
    confidence: float = Field(..., description='The confidence score of the identification.')
    subcategories: list['IdentifiedCategory'] = Field(
        default_factory=list, description='List of subcategories.'
    )


class CreateCategoriesRequest(BaseProjectRequest):
    pass


class AddCategoriesRequest(BaseProjectRequest):
    existing: list[Category] = Field(
        ..., description='Existing categories which must be excluded from the identification.'
    )


class CategoriesResponse(BaseModel):
    categories: list[IdentifiedCategory] = Field(
        ..., description='The list of identified risk categories.'
    )
