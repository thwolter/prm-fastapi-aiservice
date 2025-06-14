"""
End-to-end tests for OpenMeter service integrations.
These tests verify that the CustomerService, TokenConsumptionService, and EntitlementService
can interact with the actual OpenMeter API.
"""

import asyncio
import uuid

import pytest
from fastapi import Request
from riskgpt.models.schemas import ResponseInfo

from src.auth.schemas import EntitlementCreate
from src.auth.subject_service import SubjectService
from src.core.config import settings
from src.utils.exceptions import ExternalServiceException


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
    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature="ai_tokens", max_limit=1000, period="MONTH")
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Get the entitlement status
    status = await entitlement_service.get_token_entitlement_status(test_user_id, feature)
    assert status is True, "User should have access after setting entitlement"

    # Get the entitlement value
    value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    assert value["hasAccess"] is True, "User should have access"
    assert value["balance"] == 1000, "Balance should be 1000"

    # Test has_access alias
    has_access = await entitlement_service.has_access(test_user_id, feature)
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

    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement
    limit = EntitlementCreate(feature=feature, max_limit=1000, period="MONTH")
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Consume tokens directly
    tokens = 300

    result_info = ResponseInfo(
        consumed_tokens=tokens,
        model_name="gpt-test",
        prompt_name="e2e-test",
        total_cost=0.0,  # Assuming cost is not relevant for this test
    )

    await token_consumption_service.consume_tokens(result_info)

    # Wait for OpenMeter to update the balance (polling with timeout)
    expected_balance = 1000 - tokens
    value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    for _ in range(10):  # Try for up to ~5 seconds
        if value["balance"] == expected_balance:
            break
        await asyncio.sleep(0.5)
        value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    else:
        assert value["balance"] == expected_balance, f"Balance should be {expected_balance}"
