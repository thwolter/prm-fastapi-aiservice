from typing import Optional

from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):
    total_tokens: Optional[int] = Field(..., description='The total number of tokens.')
    total_cost: Optional[float] = Field(..., description='The total cost of the tokens.')
