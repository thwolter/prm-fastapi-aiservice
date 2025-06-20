"""
API router for payment-related endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_payment_service
from src.domain.models.payment import Payment
from src.domain.services.payment_service import PaymentService

router = APIRouter(prefix='/payments', tags=['Payments'])


@router.post('/{subscription_id}', status_code=status.HTTP_201_CREATED, response_model=Payment)
async def process_payment(
    subscription_id: UUID,
    amount: float,
    currency: str,
    payment_method: str,
    metadata: Optional[dict] = None,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Process a payment for a subscription.
    """
    try:
        payment = await payment_service.process_payment(
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            metadata=metadata,
        )
        return payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to process payment: {str(e)}',
        )


@router.get('/{payment_id}', response_model=Payment)
async def get_payment(
    payment_id: UUID,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get a payment by ID.
    """
    try:
        payment = await payment_service.get_payment(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Payment with ID {payment_id} not found',
            )
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get payment: {str(e)}',
        )


@router.get('/subscription/{subscription_id}', response_model=List[Payment])
async def get_payments_for_subscription(
    subscription_id: UUID,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get all payments for a subscription.
    """
    try:
        return await payment_service.get_payments_for_subscription(subscription_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get payments for subscription: {str(e)}',
        )


@router.post('/{payment_id}/refund', response_model=Payment)
async def refund_payment(
    payment_id: UUID,
    amount: Optional[float] = None,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Refund a payment.
    """
    try:
        payment = await payment_service.refund_payment(payment_id, amount)
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to refund payment: {str(e)}',
        )


@router.patch('/{payment_id}/status', response_model=Payment)
async def update_payment_status(
    payment_id: UUID,
    status: str,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Update the status of a payment.
    """
    try:
        payment = await payment_service.update_payment_status(payment_id, status)
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update payment status: {str(e)}',
        )
