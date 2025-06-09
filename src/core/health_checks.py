import requests
import sentry_sdk
from fastapi import APIRouter
from langchain import hub
from langchain_openai import ChatOpenAI
from openmeter import Client

from src.core.config import settings
from src.core.redis import redis_client
from src.utils.exceptions import ExternalServiceException
from src.utils.circuit_breaker import with_circuit_breaker

router = APIRouter(tags=['Health Check'])


@router.get('/health-check')
async def health_check():
    return {'status': 'ok'}


@router.get('/health-check/openai/check-connection')
@with_circuit_breaker(service_name='OpenAI')
async def check_openai_connection():
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', api_key=settings.OPENAI_API_KEY)
    try:
        response = llm.invoke(['Answer: yes'])
        if response:
            return {'message': 'OpenAI connection successful'}
        else:
            raise ExternalServiceException(detail='OpenAI connection failed', service_name='OpenAI')
    except Exception as e:
        raise ExternalServiceException(detail=str(e), service_name='OpenAI')


@router.get('/health-check/smith/check-connection')
@with_circuit_breaker(service_name='Smith')
async def check_smith_connection():
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', api_key=settings.OPENAI_API_KEY)
    try:
        prompt_template = hub.pull('health-check').template
        response = llm.invoke([prompt_template])
        if response:
            return {'message': 'Smith connection successful'}
        else:
            raise ExternalServiceException(detail='Smith connection failed', service_name='Smith')
    except requests.RequestException as e:
        raise ExternalServiceException(detail=str(e), service_name='Smith')


@router.get('/health-check/redis/check-connection')
@with_circuit_breaker(service_name='Redis')
async def check_redis_connection():
    try:
        response = redis_client.ping()
        if response:
            return {'message': 'Redis connection successful'}
        else:
            raise ExternalServiceException(detail='Redis connection failed', service_name='Redis')
    except Exception as e:
        raise ExternalServiceException(detail=str(e), service_name='Redis')


@router.get('/health-check/sentry/check-connection')
@with_circuit_breaker(service_name='Sentry')
async def check_sentry_connection():
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
async def check_openmeter_connection():
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
            client.get_meters()
            return {'message': 'OpenMeter connection successful'}
        except Exception as e:
            raise ExternalServiceException(detail=str(e), service_name='OpenMeter')
    except Exception as e:
        raise ExternalServiceException(detail=str(e), service_name='OpenMeter')
