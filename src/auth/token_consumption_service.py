"""
TokenConsumptionService: Manages token consumption via OpenMeter.
"""

import uuid

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

    def __init__(self, client: Client, async_client: AsyncClient, request: BaseResponse):
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
        self.response_info: ResponseInfo = request.state.result.response_info
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
