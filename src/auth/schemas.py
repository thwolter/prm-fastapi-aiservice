from typing import Literal, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    grant_type: Optional[str] = "password"
    username: str
    password: str


class EntitlementCreate(BaseModel):
    feature: str
    max_limit: int
    period: Literal["DAY", "WEEK", "MONTH", "YEAR"]


class ConsumedTokensInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str


class TokenQuotaResponse:
    sufficient: bool
    token_limit: int
    consumed_tokens: int
    remaining_tokens: int
