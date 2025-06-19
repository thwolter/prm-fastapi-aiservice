import uuid

import pytest
import pytest_asyncio
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from riskgpt.models.schemas import BaseResponse, default_response_info
from starlette.requests import Request

from src.auth.token_consumption_service import TokenConsumptionService
from src.core.config import settings
from src.domain.services.entitlement_service import EntitlementService
from src.domain.services.subject_service import SubjectService
from src.external.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from src.external.metering.openmeter_client import OpenMeterClient


@pytest_asyncio.fixture
def openmeter_clients():
    """
    Fixture that provides real OpenMeter clients for e2e testing.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip("OPENMETER_API_KEY not provided")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
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
    Fixture that provides a CustomerService instance with a test user.
    """
    sync_client, async_client = openmeter_clients

    # Create a request with the test user
    req = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_user_id,
                "user_email": f"test-{test_user_id}@example.com",
            },
        }
    )

    metering_client = OpenMeterClient(sync_client, async_client)
    service = SubjectService(metering_client, req)

    # Create the customer for testing
    await service.create_subject()

    yield service

    # Clean up after the test
    try:
        await service.delete_subject()
    except Exception as e:
        # Log but don't fail if cleanup fails
        print(f"Cleanup failed: {e}")


@pytest_asyncio.fixture
async def entitlement_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides an EntitlementService instance with a test user.
    """
    sync_client, async_client = openmeter_clients

    # Create a request with the test user
    req = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_user_id,
            },
        }
    )

    entitlement_client = OpenMeterEntitlementClient(sync_client, async_client)
    yield EntitlementService(entitlement_client, req)


@pytest_asyncio.fixture
async def token_consumption_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides a TokenConsumptionService instance with a test user.
    """
    sync_client, async_client = openmeter_clients

    # Create a request with the test user
    req = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_user_id,
                "response_info": BaseResponse(
                    response_info=default_response_info(),
                ),
            },
        }
    )

    yield TokenConsumptionService(sync_client, async_client, req)


@pytest_asyncio.fixture
async def bare_token_consumption_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides a TokenConsumptionService instance without a response for testing.
    """
    sync_client, async_client = openmeter_clients

    yield TokenConsumptionService(sync_client, async_client)
