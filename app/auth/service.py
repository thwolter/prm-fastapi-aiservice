import logging

import httpx
from fastapi import HTTPException, Request

from app.auth.schemas import ConsumedTokensInfo
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, request: Request):
        self.request = request
        self.auth_token = self.request.state.token
        self.user_id = self.request.state.user_id

    async def check_token_quota(self) -> bool:
        """
        Check the user's token quota via the data-service.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{settings.DATASERVICE_URL}/users/token/quota/',
                headers={'Cookie': f'auth={self.auth_token}'},
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()['sufficient']

    async def consume_tokens(self, result) -> None:
        """
        Update the user's token consumption via the data-service.
        """
        payload: dict = ConsumedTokensInfo(**result.tokens_info).model_dump()
        # result.tokens_info = None

        logger.info(f'Consuming {payload["consumed_tokens"]} tokens for {self.user_id}')
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{settings.DATASERVICE_URL}/users/token/',
                json=payload,
                headers={'Cookie': f'auth={self.auth_token}'},
            )

            if response.status_code != 201:
                logger.error(f'Failed to consume tokens for {self.user_id}')
            else:
                logger.info(f'Tokens consumed for {self.user_id}')
