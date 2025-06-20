"""
API router for subscription-related endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_subscription_service
from src.domain.models import Subscription
from src.domain.services import SubscriptionService

router = APIRouter(prefix='/subscriptions', tags=['Subscriptions'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=Subscription)
async def create_subscription(
    subject_id: UUID,
    plan_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    auto_renew: bool = False,
    metadata: Optional[dict] = None,
    amount: Optional[float] = None,
    currency: str = 'USD',
    payment_method: str = 'credit_card',
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Create a new subscription for a subject.

    If amount is provided, a payment will be processed for the subscription.
    """
    try:
        subscription = await subscription_service.create_subscription(
            subject_id=subject_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            auto_renew=auto_renew,
            metadata=metadata,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
        )
        return subscription
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create subscription: {str(e)}',
        )


@router.get('/{subscription_id}', response_model=Subscription)
async def get_subscription(
    subscription_id: UUID,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Get a subscription by ID.
    """
    try:
        subscription = await subscription_service.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Subscription with ID {subscription_id} not found',
            )
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get subscription: {str(e)}',
        )


@router.get('/subject/{subject_id}', response_model=List[Subscription])
async def get_subscriptions_for_subject(
    subject_id: UUID,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Get all subscriptions for a subject.
    """
    try:
        return await subscription_service.get_subscriptions_for_subject(subject_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get subscriptions for subject: {str(e)}',
        )


@router.patch('/{subscription_id}', response_model=Subscription)
async def update_subscription(
    subscription_id: UUID,
    status: Optional[str] = None,
    end_date: Optional[datetime] = None,
    auto_renew: Optional[bool] = None,
    metadata: Optional[dict] = None,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Update a subscription.
    """
    try:
        subscription = await subscription_service.update_subscription(
            subscription_id=subscription_id,
            status=status,
            end_date=end_date,
            auto_renew=auto_renew,
            metadata=metadata,
        )
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Subscription with ID {subscription_id} not found',
            )
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update subscription: {str(e)}',
        )


@router.post('/{subscription_id}/cancel', response_model=Subscription)
async def cancel_subscription(
    subscription_id: UUID,
    refund: bool = False,
    refund_amount: Optional[float] = None,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Cancel a subscription.

    If refund is True, a refund will be processed for the subscription.
    If refund_amount is provided, only that amount will be refunded; otherwise, the full amount will be refunded.
    """
    try:
        subscription = await subscription_service.cancel_subscription(
            subscription_id=subscription_id, refund=refund, refund_amount=refund_amount
        )
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Subscription with ID {subscription_id} not found',
            )
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to cancel subscription: {str(e)}',
        )
