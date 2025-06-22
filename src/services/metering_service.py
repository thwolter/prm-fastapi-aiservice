from typing import Any, Dict, Optional
from uuid import UUID

from openmeter.aio import Client

from models.usage import UsageEvent
from src.core.config import settings
from src.utils import logutils

logger = logutils.get_logger(__name__)


class MeteringService:
    """
    Service for managing token entitlements and consumption.
    """

    def __init__(self):
        """Initialize the MeteringService with an OpenMeter client."""
        self.client = self._create_client()

    @staticmethod
    def _create_client() -> Client:
        """Create and return an OpenMeter client."""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.OPENMETER_API_KEY}',
        }

        return Client(
            endpoint=settings.OPENMETER_API_URL,
            headers=headers,
        )

    async def check_entitlement(self, subject_id: UUID, feature_key: str = None) -> Dict[str, Any]:
        """
        Check if a subject has sufficient tokens for the specified feature.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check (defaults to settings.OPENMETER_FEATURE_KEY).

        Returns:
            Dict containing entitlement information including 'has_access' and 'balance'.
        """
        feature = feature_key or settings.OPENMETER_FEATURE_KEY
        try:
            return await self.client.get_entitlement_value(str(subject_id), feature)
        except Exception as e:
            logger.error(
                f'Error checking entitlement for subject {subject_id}, feature {feature}: {e}'
            )
            # Return a default response indicating no access
            return {'has_access': False, 'balance': 0}

    async def consume_tokens(
        self,
        subject_id: UUID,
        tokens: int,
        model: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> bool:
        """
        Consume tokens for a subject.

        Args:
            subject_id: The ID of the subject.
            tokens: Number of tokens to consume.
            model: Optional model name.
            prompt: Optional prompt name.

        Returns:
            True if tokens were successfully consumed, False otherwise.
        """
        usage_event = UsageEvent(
            tokens=tokens,
            model=model,
            prompt=prompt,
        )

        try:
            return self.client.ingest_event(
                subject_id=str(subject_id),
                usage_event=usage_event.to_dict(),
            )
        except Exception as e:
            logger.error(f'Error consuming tokens for subject {subject_id}: {e}')
            return False
