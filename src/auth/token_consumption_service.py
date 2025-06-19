"""
TokenConsumptionService: Manages token consumption via OpenMeter.
"""

import uuid
from typing import Optional
from uuid import UUID

from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from riskgpt.models.schemas import BaseResponse, ResponseInfo

from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenConsumptionService:
    """
    Service for managing token consumption in OpenMeter.
    """

    # todo: Is it really a BaseResponse? Should it be a Request with state and BaseResponse? Define a schema.
    def __init__(
        self, client: Client, async_client: AsyncClient, request: Optional[BaseResponse] = None
    ):
        """
        Initialize the TokenConsumptionService.

        Args:
            client: The OpenMeter client.
            async_client: The async OpenMeter client.
            request: The BaseResponse object containing response_info and user_id in state.
        """
        self.client = client
        self.async_client = async_client
        self.request = request
        if request:
            self.response_info: ResponseInfo = request.state.response_info
            self.user_id = request.state.user_id

    async def consume_tokens(self) -> bool:
        """
        Consumes tokens by creating and ingesting a CloudEvent to OpenMeter.

        Creates an event with token consumption data including the number of tokens,
        model name, and prompt name from the response_info. Uses the synchronous
        OpenMeter client to ingest the event.

        Returns:
            bool: True if the event was successfully ingested.
        """
        event_data = {
            "tokens": self.response_info.consumed_tokens,
            "model": self.response_info.model_name,
            "prompt": self.response_info.prompt_name,
        }

        event = CloudEvent(
            attributes={
                "id": str(uuid.uuid4()),
                "type": "tokens",
                "source": settings.OPENMETER_SOURCE,
                "subject": self.user_id,
            },
            data=event_data,
        )
        self.client.ingest_events(to_dict(event))
        return True

    async def consume_tokens_for_user(
        self,
        user_id: UUID,
        token: int,
        model_name: Optional[str] = None,
        prompt_name: Optional[str] = None,
    ) -> bool:
        """
        Consumes token for a specific user by creating and ingesting a CloudEvent to OpenMeter.

        Args:
            user_id (str): The ID of the user for whom tokens are being consumed.
            token (int): The number of tokens consumed.
            model_name (str): The name of the model used.
            prompt_name (str): The name of the prompt used.

        Returns:
            bool: True if the event was successfully ingested.
        """
        event_data = {
            "tokens": token,
            "model": model_name or "unknown_model",
            "prompt": prompt_name or "unknown_prompt",
        }

        event = CloudEvent(
            attributes={
                "id": str(uuid.uuid4()),
                "type": "tokens",
                "source": settings.OPENMETER_SOURCE,
                "subject": str(user_id),
            },
            data=event_data,
        )
        self.client.ingest_events(to_dict(event))
        return True
