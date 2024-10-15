from pydantic import BaseModel, Field

from app.services.base_service import BaseAIService


class RiskIdentificationQuery(BaseModel):
   category: str = Field(..., description="The category of the risk.")
   subcategory: str | None = Field(None, description="The subcategory of the risk.")
   context: str = Field(..., description="The context of the risk.")


class Risk(BaseModel):
    title: str = Field(..., description="The title of the risk.")
    description: str = Field(..., description="The description of the risk.")


class RiskIdentificationResult(BaseModel):
    risks: list[Risk] = Field(..., description="The list of risks identified.")


class RiskIdentificationService(BaseAIService):
    prompt_name_category = "identify-risk-for-category"
    prompt_name_categories = "identify-risk-for-categories"
    QueryModel = RiskIdentificationQuery
    ResultModel = RiskIdentificationResult

    def get_prompt_name(self, query: RiskIdentificationQuery) -> str:
        if query.subcategory:
            return self.prompt_name_categories
        return self.prompt_name_category
