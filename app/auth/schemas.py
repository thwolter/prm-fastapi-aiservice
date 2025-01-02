from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    grant_type: Optional[str] = 'password'
    username: str
    password: str


class ConsumedTokensInfo(BaseModel):
    query: Optional[str] = None
    token: int
    cost: float


class TokenQuotaResponse:
    quota: float
    consumed: int
    remaining: int
