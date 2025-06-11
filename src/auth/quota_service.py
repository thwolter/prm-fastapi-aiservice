import uuid
from typing import Any
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent
from fastapi import Request
from openmeter import Client

from src.auth.schemas import ConsumedTokensInfo
from src.core.config import settings
from src.utils import logutils
from src.utils.exceptions import RequestException, ResourceNotFoundException

logger = logutils.get_logger(__name__)


class TokenQuotaService:
    def __init__(self, request: Request):
        self.request = request

        # In a local environment, use dummy values if token or user_id are not set
        if settings.ENVIRONMENT == "local":
            self.auth_token = getattr(self.request.state, "token", "dummy_token")
            self.user_id = getattr(
                self.request.state, "user_id", "00000000-0000-0000-0000-000000000000"
            )
        else:
            self.auth_token = self.request.state.token
            self.user_id = self.request.state.user_id

        self.client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.OPENMETER_API_KEY}",
            },
        )

    async def has_access(self) -> bool:
        """
        Check the user's token quota via the data-service.
        In the local environment, token quota checking is bypassed.
        """
        # Skip token quota checking in local environment
        if settings.ENVIRONMENT == "local":
            logger.debug("Bypassing token quota check in local environment")
            return True

        try:
            response = self.client.get_entitlement_value(str(self.user_id), "ai_tokens")
        except ResourceNotFoundError as e:
            logger.error(f"User {self.user_id}: {e}")
            raise ResourceNotFoundException(detail="User not found")
        return bool(response["hasAccess"])

    async def consume_tokens(self, result: Any, user_id: UUID) -> None:
        """
        Update the user's token consumption via the data-service.
        In a local environment, token consumption is bypassed.
        """
        # Skip token consumption in local environment
        if settings.ENVIRONMENT == "local":
            logger.debug("Bypassing token consumption in local environment")
            # Still need to clean up tokens_info from result
            if hasattr(result, "tokens_info"):
                del result.tokens_info
            return

        try:
            payload = ConsumedTokensInfo(**result.tokens_info)
            del result.tokens_info
        except ValueError as e:
            logger.error(f"Invalid tokens info: {e}")
            raise RequestException(detail="Invalid tokens info")

        response_info = getattr(result, "response_info", None)

        event_data = {
            "tokens": payload.total_tokens,
            "model": payload.model_name,
            "prompt": payload.prompt_name,
        }
        if response_info is not None:
            event_data["response_info"] = response_info

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
