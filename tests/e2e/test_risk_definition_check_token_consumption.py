"""
Integration tests for RiskDefinitionCheckService with token consumption.
"""

import asyncio
import uuid

import pytest
import pytest_asyncio
from fastapi import Request
from riskgpt.models.schemas import BusinessContext, DefinitionCheckRequest

from src.auth.schemas import EntitlementCreate
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.core.config import settings
from src.middleware.token_entitlement_check import TokenEntitlementCheckMiddleware
from src.services.services import RiskDefinitionCheckService


@pytest_asyncio.fixture
async def risk_definition_check_service(test_user_id) -> RiskDefinitionCheckService:
    """
    Create a RiskDefinitionCheckService instance for testing.
    """
    # Set up the token quota service provider with the test user ID
    TokenQuotaServiceProvider.setup_for_testing(test_user_id)

    return RiskDefinitionCheckService()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_risk_definition_check_sufficient_tokens(
    subject_service,
    entitlement_service,
    token_consumption_service,
    risk_definition_check_service,
    test_user_id,
):
    """
    Test that RiskDefinitionCheckService correctly consumes tokens when a user has sufficient tokens.

    Steps:
    1. Create a user (done via fixtures)
    2. Assign entitlement with sufficient tokens
    3. Call the RiskDefinitionCheckService
    4. Verify token consumption in OpenMeter
    """

    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement with sufficient tokens (1000)
    limit = EntitlementCreate(feature=feature, max_limit=1000, period="MONTH")
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Get initial balance
    initial_value = await entitlement_service.get_entitlement_value(test_user_id, feature)
    initial_balance = initial_value["balance"]

    # Create a test request for the RiskDefinitionCheckService
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id=str(uuid.uuid4()),
            project_description="Test project description",
        ),
        risk_description="This is a test risk description for token consumption testing.",
    )

    # Call the service
    response = await risk_definition_check_service.execute_query(request)

    # Verify the response
    assert response is not None
    assert hasattr(response, "response_info")
    assert response.response_info.consumed_tokens > 0

    # Wait for OpenMeter to update the balance (polling with timeout)
    expected_balance = initial_balance - response.response_info.consumed_tokens
    for _ in range(10):  # Try for up to ~5 seconds
        value = await entitlement_service.get_entitlement_value(test_user_id, feature)
        if value["balance"] <= expected_balance:
            break
        await asyncio.sleep(0.5)
    else:
        value = await entitlement_service.get_entitlement_value(test_user_id, feature)

    # Verify token consumption
    assert value["balance"] <= initial_balance, "Tokens should have been consumed"
    assert value["balance"] <= expected_balance, f"Balance should be at most {expected_balance}"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_risk_definition_check_insufficient_tokens(
    subject_service, entitlement_service, token_consumption_service, test_user_id
):
    """
    Test that requests are rejected when a user has insufficient tokens.

    Steps:
    1. Create a user (done via fixtures)
    2. Assign entitlement with insufficient tokens (0)
    3. Create a request with the middleware active
    4. Verify the request is rejected with an appropriate message
    """
    feature = settings.OPENMETER_FEATURE_KEY

    # Set an entitlement with insufficient tokens (0)
    limit = EntitlementCreate(feature=feature, max_limit=0, period="MONTH")
    await entitlement_service.set_entitlement(test_user_id, limit)

    # Create a request with the middleware
    req = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/api/risk/check/definition/",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_user_id,
            },
        }
    )

    # Create the middleware
    middleware = TokenEntitlementCheckMiddleware(None)

    # Mock the call_next function to return a success response
    async def mock_call_next(request):
        return {"status": "success"}

    # Call the middleware
    response = await middleware.dispatch(req, mock_call_next)

    # Verify the response is a 403 Forbidden with the appropriate message
    assert response.status_code == 403
    response_body = await response.json()
    assert "Insufficient token balance" in response_body["detail"]
