import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from riskgpt.models.schemas import BaseResponse, default_response_info
from starlette.requests import Request

from src.core.config import settings
from src.domain.services.entitlement_service import EntitlementService
from src.domain.services.metering_service import MeteringService
from src.external.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from src.external.metering.openmeter_client import OpenMeterClient


@pytest_asyncio.fixture
def openmeter_clients():
    """
    Fixture that provides real OpenMeter clients for e2e testing.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    sync_client = Client(endpoint=settings.OPENMETER_API_URL, headers=headers)
    async_client = AsyncClient(endpoint=settings.OPENMETER_API_URL, headers=headers)

    return sync_client, async_client


@pytest.fixture
def test_user_id():
    """
    Fixture that provides a unique user ID for testing.
    """
    return uuid.uuid4()


@pytest_asyncio.fixture
async def subject_service(openmeter_clients, test_user_id):
    """
    Fixture that provides a mock subject service with a test user.
    This replaces the previous SubjectService implementation.
    """
    sync_client, async_client = openmeter_clients
    metering_client = OpenMeterClient(sync_client, async_client)

    # Create a mock subject service
    mock_subject_service = MagicMock()
    mock_subject_service.user_id = test_user_id
    mock_subject_service.user_email = f'test-{test_user_id}@example.com'
    mock_subject_service.metering_client = metering_client

    # Mock the create_subject method
    create_subject_mock = AsyncMock()
    mock_subject_service.create_subject = create_subject_mock

    # Mock the delete_subject method
    delete_subject_mock = AsyncMock()
    mock_subject_service.delete_subject = delete_subject_mock

    # Create the subject in OpenMeter directly
    # Note: These methods are not part of AbstractMeteringClient but are used in tests
    try:
        # Create test subject if the OpenMeter client supports it
        if hasattr(metering_client, 'upsert_subject'):
            metering_client.upsert_subject(
                [{'key': str(test_user_id), 'displayName': f'test-{test_user_id}@example.com'}]
            )
    except Exception as e:
        print(f'Warning: Could not create subject: {e}')

    yield mock_subject_service

    # Clean up after the test
    try:
        # Delete test subject if the OpenMeter client supports it
        if hasattr(metering_client, 'delete_subject'):
            metering_client.delete_subject(str(test_user_id))
    except Exception as e:
        # Log but don't fail if cleanup fails
        print(f'Cleanup failed: {e}')


@pytest_asyncio.fixture
async def entitlement_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides an EntitlementService instance with a test user.
    """
    sync_client, async_client = openmeter_clients

    # Create a request with the test user
    req = Request(
        scope={
            'type': 'http',
            'method': 'POST',
            'path': '/test',
            'headers': [(b'accept', b'application/json')],
            'state': {
                'token': 'test_token',
                'user_id': test_user_id,
            },
        }
    )

    entitlement_client = OpenMeterEntitlementClient(sync_client, async_client)
    yield EntitlementService(entitlement_client, req)


@pytest_asyncio.fixture
async def metering_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides a MeteringService instance with a test user.
    """
    sync_client, async_client = openmeter_clients

    # Create a request with the test user
    req = Request(
        scope={
            'type': 'http',
            'method': 'POST',
            'path': '/test',
            'headers': [(b'accept', b'application/json')],
            'state': {
                'token': 'test_token',
                'user_id': test_user_id,
                'response_info': BaseResponse(
                    response_info=default_response_info(),
                ),
            },
        }
    )

    metering_client = OpenMeterClient(sync_client, async_client)
    yield MeteringService(metering_client, req)


@pytest_asyncio.fixture
async def bare_metering_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides a MeteringService instance without a response for testing.
    """
    sync_client, async_client = openmeter_clients
    metering_client = OpenMeterClient(sync_client, async_client)

    yield MeteringService(metering_client)
