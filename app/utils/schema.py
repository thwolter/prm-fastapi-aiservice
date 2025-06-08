from typing import Optional

from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):
    tokens_info: Optional[dict] = Field(
        ..., description='The tokens consumed by the user.'
    )
    response_info: Optional[dict] = Field(
        default=None, description='Additional response information.'
    )
