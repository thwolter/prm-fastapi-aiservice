import sentry_sdk
from fastapi import APIRouter
from openmeter.aio import Client

from src.core.config import settings
from src.utils.circuit_breaker import with_circuit_breaker
from src.utils.exceptions import ExternalServiceException

router = APIRouter(tags=['Health Check'])


@router.get('/health-check')
async def health_check() -> dict:
    return {'status': 'ok'}


@router.get('/health-check/sentry/check-connection')
@with_circuit_breaker(service_name='Sentry')
async def check_sentry_connection() -> dict:
    try:
        # Test if Sentry client is properly configured
        if sentry_sdk.Hub.current.client and sentry_sdk.Hub.current.client.dsn:
            return {'message': 'Sentry connection successful'}
        else:
            raise ExternalServiceException(detail='Sentry not configured', service_name='Sentry')
    except Exception as e:
        raise ExternalServiceException(detail=str(e), service_name='Sentry')


@router.get('/health-check/openmeter/check-connection')
@with_circuit_breaker(service_name='OpenMeter')
async def check_openmeter_connection() -> dict:
    try:
        client = Client(
            endpoint=settings.OPENMETER_API_URL,
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {settings.OPENMETER_API_KEY}',
            },
        )
        # Make a simple request to check connectivity
        # Using a try/except block to catch any exceptions from the API call
        try:
            # Get meters list as a simple API call to verify connectivity
            await client.list_meters()
            return {'message': 'OpenMeter connection successful'}
        except Exception as e:
            raise ExternalServiceException(detail=str(e), service_name='OpenMeter')
    except Exception as e:
        raise ExternalServiceException(detail=str(e), service_name='OpenMeter')
