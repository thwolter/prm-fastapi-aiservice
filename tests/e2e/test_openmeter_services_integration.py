"""
End-to-end tests for OpenMeter service integrations.
These tests verify that the CustomerService, TokenConsumptionService, and EntitlementService
can interact with the actual OpenMeter API.
"""

import uuid

import pytest
from fastapi import Request
from openmeter import Client
from openmeter.aio import Client as AsyncClient
from riskgpt.models.schemas import ResponseInfo

from src.auth.entitlement_service import EntitlementService
from src.auth.schemas import EntitlementCreate
from src.auth.subject_service import SubjectService
from src.auth.token_consumption_service import TokenConsumptionService
from src.core.config import settings
from src.utils.exceptions import ExternalServiceException


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
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


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_customer_service_create_delete(openmeter_clients):
    """
    Test that CustomerService can create and delete customers in OpenMeter.
    """
    sync_client, async_client = openmeter_clients
    test_id = uuid.uuid4()
    test_email = f"test-{test_id}@example.com"

    # Create a request with a test user
    req = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_id,
                "user_email": test_email,
            },
        }
    )

    service = SubjectService(sync_client, async_client, req)

    # Create the customer
    await service.create_subject()

    # Delete the customer
    await service.delete_subject()

    # Verify deletion by attempting to delete again, which should raise an exception
    with pytest.raises(ExternalServiceException):
        await service.delete_subject()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_entitlement_service_set_get(subject_service, entitlement_service, test_user_id):
    """
    Test that EntitlementService can set and get entitlements in OpenMeter.
    """
    # Await the async generator fixture to get the service instance
    service = await anext(entitlement_service)

    # Set an entitlement
    limit = EntitlementCreate(feature="ai_tokens", max_limit=1000, period="MONTH")
    await service.set_entitlement(limit)

    # Get the entitlement status
    status = await service.get_token_entitlement_status()
    assert status is True, "User should have access after setting entitlement"

    # Get the entitlement value
    value = await service.get_entitlement_value(test_user_id)
    assert value["hasAccess"] is True, "User should have access"
    assert value["balance"] == 1000, "Balance should be 1000"

    # Test has_access alias
    has_access = await service.has_access()
    assert has_access is True, "has_access should return True"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_token_consumption_consume_tokens(
    subject_service, entitlement_service, token_consumption_service, test_user_id
):
    """
    Test that TokenConsumptionService can consume tokens directly in OpenMeter.
    """

    feature = "ai_tokens"

    # Await the async generator fixture to get the service instance
    entitlement_service = await anext(entitlement_service)
    token_consumption_service = await anext(token_consumption_service)

    # Set an entitlement
    limit = EntitlementCreate(feature=feature, max_limit=1000, period="MONTH")
    await entitlement_service.set_entitlement(limit)

    # Consume tokens directly
    tokens = 300

    result_info = ResponseInfo(
        consumed_tokens=tokens,
        model_name="gpt-test",
        prompt_name="e2e-test",
        total_cost=0.0,  # Assuming cost is not relevant for this test
    )

    await token_consumption_service.consume_tokens(result_info)

    # Check balance after consumption
    value = await entitlement_service.get_entitlement_value(test_user_id)
    assert value["balance"] == 1000 - tokens, f"Balance should be {1000 - tokens}"
