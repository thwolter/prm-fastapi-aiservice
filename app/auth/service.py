import logging
from uuid import UUID

import httpx
from fastapi import HTTPException, Request

from app.auth.schemas import ConsumedTokensInfo
from app.core.config import settings

logger = logging.getLogger(__name__)

QUOTA_ENDPOINT = f'{settings.DATASERVICE_URL}/token/quota/'
CONSUME_ENDPOINT = f'{settings.DATASERVICE_URL}/token/consume/'


class AuthService:
    def __init__(self, request: Request):
        self.request = request
        self.auth_token = self.request.state.token
        self.user_id = self.request.state.user_id

    async def check_token_quota(self, user_id: UUID) -> bool:
        """
        Check the user's token quota via the data-service.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(QUOTA_ENDPOINT, headers={'Cookie': f'auth={self.auth_token}'})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()['sufficient']

    async def consume_tokens(self, result, user_id: UUID) -> None:
        """
        Update the user's token consumption via the data-service.
        """
        payload: dict = ConsumedTokensInfo(**result.tokens_info).model_dump()
        payload['user_id'] = user_id

        consumed_tokens = payload["consumed_tokens"]
        logger.info(f'Consuming {consumed_tokens} tokens for {self.user_id}')
        async with httpx.AsyncClient() as client:
            response = await client.post(
                CONSUME_ENDPOINT,
                json=payload,
                headers={'Cookie': f'auth={self.auth_token}'},
            )

            if response.status_code != 201:
                logger.error(f'Failed to consume tokens for {self.user_id}')
            else:
                logger.info(f'{consumed_tokens} Tokens consumed for {self.user_id}')
