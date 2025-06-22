"""
API router for metering-related endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_metering_service
from src.models.usage import UsageEvent
from src.services.metering_service import MeteringService

router = APIRouter(prefix='/metering', tags=['Metering'])


@router.post('/record-usage', status_code=status.HTTP_201_CREATED)
async def record_usage(
    usage_event: UsageEvent,
    subject_id: UUID,
    metering_service: MeteringService = Depends(get_metering_service),
):
    """
    Record usage for a subject.
    """
    try:
        success = await metering_service.consume_tokens(
            subject_id=subject_id,
            tokens=usage_event.tokens,
            model=usage_event.model,
            prompt=usage_event.prompt,
        )
        if success:
            return {'message': 'Usage recorded successfully'}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to record usage',
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to record usage: {str(e)}',
        )
