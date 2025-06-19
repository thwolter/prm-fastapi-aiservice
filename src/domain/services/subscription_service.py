"""
SubscriptionService: Manages subscriptions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.models import Subscription
from src.utils import logutils

logger = logutils.get_logger(__name__)


class SubscriptionService:
    """
    Service for managing subscriptions.
    """

    def __init__(self):
        """
        Initialize the SubscriptionService.
        """
        # This is a placeholder. In a real implementation, this would likely
        # use a database or external service to store and retrieve subscriptions.
        self.subscriptions = {}

    async def create_subscription(
        self,
        subject_id: UUID,
        plan_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        auto_renew: bool = False,
        metadata: Optional[dict] = None,
    ) -> Subscription:
        """
        Create a new subscription.

        Args:
            subject_id: The ID of the subject (user).
            plan_id: The ID of the plan.
            start_date: The start date of the subscription. Defaults to now.
            end_date: The end date of the subscription.
            auto_renew: Whether the subscription should auto-renew.
            metadata: Additional metadata for the subscription.

        Returns:
            The created subscription.
        """
        from uuid import uuid4

        subscription_id = uuid4()
        subscription = Subscription(
            id=subscription_id,
            subject_id=subject_id,
            plan_id=plan_id,
            status="active",
            start_date=start_date or datetime.now(),
            end_date=end_date,
            auto_renew=auto_renew,
            metadata=metadata or {},
        )

        # In a real implementation, this would save to a database
        self.subscriptions[str(subscription_id)] = subscription
        return subscription

    async def get_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """
        Get a subscription by ID.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            The subscription, or None if not found.
        """
        return self.subscriptions.get(str(subscription_id))

    async def get_subscriptions_for_subject(self, subject_id: UUID) -> List[Subscription]:
        """
        Get all subscriptions for a subject.

        Args:
            subject_id: The ID of the subject.

        Returns:
            A list of subscriptions for the subject.
        """
        return [
            subscription
            for subscription in self.subscriptions.values()
            if subscription.subject_id == subject_id
        ]

    async def update_subscription(
        self,
        subscription_id: UUID,
        status: Optional[str] = None,
        end_date: Optional[datetime] = None,
        auto_renew: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[Subscription]:
        """
        Update a subscription.

        Args:
            subscription_id: The ID of the subscription.
            status: The new status of the subscription.
            end_date: The new end date of the subscription.
            auto_renew: Whether the subscription should auto-renew.
            metadata: Additional metadata for the subscription.

        Returns:
            The updated subscription, or None if not found.
        """
        subscription = self.subscriptions.get(str(subscription_id))
        if not subscription:
            return None

        if status is not None:
            subscription.status = status
        if end_date is not None:
            subscription.end_date = end_date
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
        if metadata is not None:
            subscription.metadata = metadata

        # In a real implementation, this would update in a database
        self.subscriptions[str(subscription_id)] = subscription
        return subscription

    async def cancel_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """
        Cancel a subscription.

        Args:
            subscription_id: The ID of the subscription.

        Returns:
            The cancelled subscription, or None if not found.
        """
        return await self.update_subscription(subscription_id, status="cancelled")
