import logging

import httpx
from fastapi import HTTPException

from app.auth.schemas import ConsumedTokensInfo
from app.core.config import settings

DATA_SERVICE_URL = settings.DATASERVICE_URL

logger = logging.getLogger(__name__)


async def check_token_quota(token: str) -> int:
    """
    Check the user's token quota via the data-service.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{DATA_SERVICE_URL}/users/token/quota/', headers={'Cookie': f'auth={token}'}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail='Failed to fetch token quota')
        return response.json()['quota']


async def consume_tokens(token: str, user_id: str, tokens_info: dict | None = None) -> None:
    """
    Update the user's token consumption via the data-service.
    """

    if tokens_info is not None:
        payload = ConsumedTokensInfo(
            token=tokens_info['token'], cost=tokens_info['cost'], query=tokens_info['query']
        ).model_dump()

        logger.info(f'Consuming {tokens_info["token"]} tokens for {user_id}')
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{DATA_SERVICE_URL}/users/token/',
                json=payload,
                headers={'Cookie': f'auth={token}'},
            )

            if response.status_code != 201:
                logger.error(f'Failed to consume tokens for {user_id}')
            else:
                logger.info(f'Tokens consumed for {user_id}')
