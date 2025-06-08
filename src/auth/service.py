import logging
import uuid
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from fastapi import HTTPException, Request
from openmeter import Client

from src.auth.schemas import ConsumedTokensInfo
from src.core.config import settings

logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self, request: Request):
        self.request = request
        self.auth_token = self.request.state.token
        self.user_id = self.request.state.user_id

        self.client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {settings.OPENMETER_API_KEY}',
            },
        )

    async def has_access(self) -> bool:
        """
        Check the user's token quota via the data-service.
        """
        try:
            response = self.client.get_entitlement_value(str(self.user_id), 'ai_tokens')
        except ResourceNotFoundError as e:
            logger.error(f'User {self.user_id}: {e}')
            raise HTTPException(status_code=404, detail='User not found')
        return response['hasAccess']

    async def consume_tokens(self, result, user_id: UUID) -> None:
        """
        Update the user's token consumption via the data-service.
        """
        try:
            payload = ConsumedTokensInfo(**result.tokens_info)
            del result.tokens_info
        except ValueError as e:
            logger.error(f'Invalid tokens info: {e}')
            raise HTTPException(status_code=400, detail='Invalid tokens info')

        response_info = getattr(result, 'response_info', None)

        event_data = {
            'tokens': payload.total_tokens,
            'model': payload.model_name,
            'prompt': payload.prompt_name,
        }
        if response_info is not None:
            event_data['response_info'] = response_info

        event = CloudEvent(
            attributes={
                'id': str(uuid.uuid4()),
                'type': 'tokens',
                'source': settings.OPENMETER_SOURCE,
                'subject': str(user_id),
            },
            data=event_data,
        )

        self.client.ingest_events(to_dict(event))
