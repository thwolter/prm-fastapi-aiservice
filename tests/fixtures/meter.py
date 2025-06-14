import uuid

import pytest
import pytest_asyncio
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from starlette.requests import Request

from auth.entitlement_service import EntitlementService
from auth.subject_service import SubjectService
from auth.token_consumption_service import TokenConsumptionService
from core.config import settings


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

    service = SubjectService(sync_client, async_client, req)

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

    yield EntitlementService(sync_client, async_client, req)


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
            },
        }
    )

    yield TokenConsumptionService(sync_client, async_client, req)
