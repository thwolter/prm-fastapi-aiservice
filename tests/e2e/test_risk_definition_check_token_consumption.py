"""
Integration tests for RiskDefinitionCheckService with token consumption.
"""

import asyncio
import uuid
from datetime import datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from riskgpt.models.schemas import (
    BusinessContext,
    DefinitionCheckRequest,
    DefinitionCheckResponse,
    ResponseInfo,
)

from src.auth.schemas import EntitlementCreate
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.core.config import settings
from src.main import app
from src.services.services import RiskDefinitionCheckService

client = TestClient(app)


@pytest_asyncio.fixture
async def risk_definition_check_service(test_user_id) -> RiskDefinitionCheckService:
    """
    Create a RiskDefinitionCheckService instance for testing.
    """
    # Set up the token quota service provider with the test user ID
    TokenQuotaServiceProvider.setup_for_testing(test_user_id)

    return RiskDefinitionCheckService()


def create_mock_definition_response(consumed_tokens):
    return DefinitionCheckResponse(
        revised_description="Text for token consumption testing.",
        biases=["None detected"],
        rationale="Valid risk statement.",
        response_info=ResponseInfo(
            consumed_tokens=consumed_tokens,
            total_cost=0.002,
            prompt_name="definition_check",
            model_name="gpt-4",
            error="",
        ),
    )


async def call_risk_definition_check(client, payload, headers):
    response = client.post("/api/risk/check/definition/", json=payload, headers=headers)
    assert response is not None
    return response.json()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures("e2e_environment")
async def test_risk_definition_check_sufficient_tokens(
    subject_service,
    entitlement_service,
    configure_mock_handle,
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

    mock_response = create_mock_definition_response(consumed_tokens=100)

    # Configure the mock with a return value
    configure_mock_handle(return_value=mock_response)

    # Set an entitlement with sufficient tokens (1000)
    limit = EntitlementCreate(feature=feature, max_limit=1000, period="MONTH")
    await entitlement_service.set_entitlement(limit)

    # Get initial balance
    initial_value = await entitlement_service.get_entitlement_value(feature)
    initial_balance = initial_value["balance"]

    # Create a test request for the RiskDefinitionCheckService
    payload = DefinitionCheckRequest(
        business_context=BusinessContext(
            model_version="1.0",
            project_id=str(uuid.uuid4()),
        ),
        risk_description="Test risk description for token consumption.",
    ).model_dump()

    auth_headers = await get_auth_token(test_user_id)

    json_response = await call_risk_definition_check(client, payload, auth_headers)
    response_info = ResponseInfo.model_validate(json_response.get("response_info"))

    # Wait for OpenMeter to update the balance (polling with timeout)
    expected_balance = initial_balance - response_info.consumed_tokens
    for _ in range(10):  # Try for up to ~5 seconds
        value = await entitlement_service.get_entitlement_value(feature)
        if value["balance"] <= expected_balance:
            break
        await asyncio.sleep(0.5)
    else:
        value = await entitlement_service.get_entitlement_value(feature)

    # Verify token consumption
    assert value["balance"] <= initial_balance, "Tokens should have been consumed"
    assert value["balance"] <= expected_balance, f"Balance should be at most {expected_balance}"


async def get_auth_token(test_user_id: uuid.UUID) -> dict:
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        "sub": str(test_user_id),
        "email": "test@example.com",
        "exp": expiry,
        "aud": settings.AUTH_TOKEN_AUDIENCE,
    }
    # Encode the token
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.AUTH_TOKEN_ALGORITHM,
    )

    auth_headers = {"Authorization": f"Bearer {token}"}

    return auth_headers


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
    await entitlement_service.set_entitlement(limit)

    # Create a test request for the RiskDefinitionCheckService
    payload = DefinitionCheckRequest(
        business_context=BusinessContext(
            model_version="1.0",
            project_id=str(uuid.uuid4()),
        ),
        risk_description="Test risk description for insufficient tokens.",
    ).model_dump()

    auth_headers = await get_auth_token(test_user_id)

    # Call the service (expecting failure due to no tokens)
    response = client.post("/api/risk/check/definition/", json=payload, headers=auth_headers)

    # Verify the response is a 403 Forbidden with the appropriate message
    assert response.status_code == 403
    response_body = response.json()
    assert "Insufficient token balance" in response_body.get("detail", "")
