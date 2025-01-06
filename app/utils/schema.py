from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):
    tokens_info: dict | None = Field(..., description='The tokens consumed by the user.')
