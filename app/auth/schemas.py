from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    grant_type: Optional[str] = 'password'
    username: str
    password: str


class ConsumedTokensInfo(BaseModel):
    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str


class TokenQuotaResponse:
    sufficient: bool
    token_limit: int
    consumed_tokens: int
    remaining_tokens: int
