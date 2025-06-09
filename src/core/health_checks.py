import requests
from fastapi import APIRouter
from langchain import hub
from langchain_openai import ChatOpenAI

from src.core.config import settings
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
