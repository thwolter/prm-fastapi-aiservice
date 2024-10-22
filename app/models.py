from pydantic import BaseModel, Field


class RiskDefinitionCheckResult(BaseModel):
    is_valid: bool = Field(..., description="Whether the text is valid or not.")
    classification: str = Field(..., description="The classification of the text.")
    original: str = Field(..., description="The original text.")
    suggestion: str = Field(..., description="Suggestions for a revised risk definition.")
    explanation: str = Field(..., description="Explanation of the classification.")


class RiskDefinitionCheckQuery(BaseModel):
    text: str = Field(..., description="The text to be assessed.")


class RiskDefinitionCheckResponse(RiskDefinitionCheckResult):
    pass


class RiskDefinitionCheckRequest(RiskDefinitionCheckQuery):
    pass


class RiskIdentificationQuery(BaseModel):
   category: str = Field(..., description="The category of the risk.")
   subcategory: str | None = Field(None, description="The subcategory of the risk.")
   context: str = Field(..., description="The context of the risk.")


class Risk(BaseModel):
    title: str = Field(..., description="The title of the risk.")
    description: str = Field(..., description="The description of the risk.")


class RiskIdentificationResult(BaseModel):
    risks: list[Risk] = Field(..., description="The list of risks identified.")


class CategoriesIdentificationQuery(BaseModel):
    text: str = Field(..., description="The text to be used for category identification.")


class Category(BaseModel):
    name: str = Field(..., description="The name of the category.")
    description: str = Field(..., description="The description of the category.")
    examples: list[str] = Field(..., description="Examples of the category.")


class CategoriesIdentificationResult(BaseModel):
    categories: list[Category] = Field(..., description="The list of categories identified.")


class CategoriesIdentificationResponse(CategoriesIdentificationResult):
    pass

class CategoriesIdentificationRequest(CategoriesIdentificationQuery):
    pass