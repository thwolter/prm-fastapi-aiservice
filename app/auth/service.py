import logging
import uuid
from uuid import UUID

import httpx
from fastapi import HTTPException, Request

from app.auth.schemas import ConsumedTokensInfo
from app.core.config import settings

from openmeter import Client
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_dict

logger = logging.getLogger(__name__)

QUOTA_ENDPOINT = f'{settings.DATASERVICE_URL}/token/quota/'
CONSUME_ENDPOINT = f'{settings.DATASERVICE_URL}/token/consume/'





class AuthService:
    def __init__(self, request: Request):
        self.request = request
        self.auth_token = self.request.state.token
        self.user_id = self.request.state.user_id

        self.client = Client(
            endpoint="https://openmeter.cloud",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.OPENMETER_API_KEY}",
            },
        )

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
        payload = ConsumedTokensInfo(**result.tokens_info)

        event = CloudEvent(
            attributes={
                "id": str(uuid.uuid4()),
                "type": "tokens",
                "source": "prm-ai-service",
                "subject": str(user_id),
            },
            data={
                'tokens': payload.total_tokens,
                'model': payload.model_name,
                'prompt': payload.prompt_name,
            },
        )

        self.client.ingest_events(to_dict(event))

