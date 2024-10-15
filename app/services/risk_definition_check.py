from pydantic import BaseModel, Field

from app.services.base_service import BaseAIService


class RiskDefinitionCheckQuery(BaseModel):
    text: str = Field(..., description="The text to be assessed.")


class RiskDefinitionCheckResult(BaseModel):
    is_valid: bool = Field(..., description="Whether the text is valid or not.")
    classification: str = Field(..., description="The classification of the text.")
    original: str = Field(..., description="The original text.")
    suggestion: str = Field(..., description="Suggestions for a revised risk definition.")
    explanation: str = Field(..., description="Explanation of the classification.")


class RiskDefinitionService(BaseAIService):
    prompt_name = "risk-definition-check"
    QueryModel = RiskDefinitionCheckQuery
    ResultModel = RiskDefinitionCheckResult
