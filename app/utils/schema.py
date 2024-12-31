from typing import Optional

from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):
    tokens: dict = Field(..., description='The tokens consumed by the user.')
