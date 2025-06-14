"""
TokenConsumptionService: Manages token consumption via OpenMeter.
"""

import uuid
from typing import Optional
from uuid import UUID

from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from riskgpt.models.schemas import ResponseInfo

from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class TokenConsumptionService:
    """
    Service for managing token consumption in OpenMeter.
    """

    def __init__(
        self, client: Client, async_client: AsyncClient, request: Optional[Request] = None
    ):
        """
        Initialize the TokenConsumptionService.

        Args:
            client: The OpenMeter client.
            async_client: The async OpenMeter client.
            request: Optional FastAPI request object.
        """
        self.client = client
        self.async_client = async_client
        self.request = request

        if request:
            self.user_id = request.state.user_id
        else:
            self.user_id = None

        self._reserved_tokens: int = 0

    @property
    def is_local_env(self) -> bool:
        """
        Check if the current environment is local.

        Returns:
            True if the environment is local, False otherwise.
        """
        return settings.ENVIRONMENT == "local"

    async def consume_tokens(
        self,
        response_info: ResponseInfo = None,
        token: Optional[int | None] = None,
        user_id: Optional[UUID] = None,
    ) -> bool:

        if not self.request and not user_id:
            logger.warning("No request or user_id provided for token consumption.")
            return False

        event_data = {
            "tokens": token if token is not None else response_info.consumed_tokens,
            "model": getattr(response_info, "model_name", ""),
            "prompt": getattr(response_info, "prompt_name", ""),
        }

        user_id_str = str(user_id or self.user_id)

        event = CloudEvent(
            attributes={
                "id": str(uuid.uuid4()),
                "type": "tokens",
                "source": settings.OPENMETER_SOURCE,
                "subject": user_id_str,
            },
            data=event_data,
        )
        self.client.ingest_events(to_dict(event))
        return True
