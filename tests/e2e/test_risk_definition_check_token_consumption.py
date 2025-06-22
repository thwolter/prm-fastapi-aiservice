"""
Integration tests for RiskDefinitionCheckService with token consumption.
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
import pytest
import pytest_asyncio
from billing_services.models import Entitlement
from fastapi.testclient import TestClient
from riskgpt.models.schemas import DefinitionCheckResponse, ResponseInfo

from src.core.config import settings
from src.main import app
from src.services.services import RiskDefinitionCheckService

client = TestClient(app)


@pytest_asyncio.fixture
async def risk_definition_check_service(test_user_id) -> RiskDefinitionCheckService:
    """
    Create a RiskDefinitionCheckService instance for testing.
    """
    return RiskDefinitionCheckService()


@pytest.fixture
def mock_get_entitlement_value():
    """
    Fixture that mocks the EntitlementService.get_entitlement_value method.

    Returns:
        A mock object that can be configured with return_value or side_effect.
    """
    with patch(
        'billing_services.services.entitlement_service.EntitlementService.get_entitlement_value'
    ) as mock_get_entitlement:
        # Default to a sufficient token balance
        mock_get_entitlement.return_value = Entitlement(
            feature_key=settings.OPENMETER_FEATURE_KEY,
            has_access=True,
            balance=100,
            limit=1000,
            usage=900,
            period='MONTH',
        )
        yield mock_get_entitlement


def create_mock_definition_response(consumed_tokens):
    return DefinitionCheckResponse(
        revised_description='Text for token consumption testing.',
        biases=['None detected'],
        rationale='Valid risk statement.',
        response_info=ResponseInfo(
            consumed_tokens=consumed_tokens,
            total_cost=0.002,
            prompt_name='definition_check',
            model_name='gpt-4',
            error='',
        ),
    )


async def call_risk_definition_check(client, payload, headers):
    response = client.post('/api/risk/check/definition/', json=payload, headers=headers)
    assert response is not None
    return response.json()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_risk_definition_check_sufficient_tokens(
    subject_service,
    entitlement_service,
    configure_mock_handle,
    risk_definition_check_service,
    test_user_id,
    mock_get_entitlement_value,
):
    """
    Test that RiskDefinitionCheckService correctly consumes tokens when a user has sufficient tokens.
    """
    # Configure the mock to return a response with consumed tokens
    consumed_tokens = 50
    mock_response = create_mock_definition_response(consumed_tokens)
    configure_mock_handle(return_value=mock_response)

    # Create a request payload
    payload = {
        'business_context': {
            'project_id': 'test-project',
            'project_description': 'Test project description',
            'domain_knowledge': 'Test domain knowledge',
            'language': 'en',
        },
        'risk_description': 'Test risk description',
    }

    # Get auth headers for the test user
    auth_headers = await get_auth_token(test_user_id)

    # Call the risk definition check endpoint
    response_data = await call_risk_definition_check(client, payload, auth_headers)

    # Verify the response
    assert response_data is not None
    assert 'revised_description' in response_data
    assert response_data['revised_description'] == 'Text for token consumption testing.'
    assert 'response_info' in response_data
    assert response_data['response_info']['consumed_tokens'] == consumed_tokens

    # Verify that the entitlement service was called to check the token balance
    mock_get_entitlement_value.assert_called_with(
        subject_id=test_user_id, feature_key=settings.OPENMETER_FEATURE_KEY
    )


async def get_auth_token(test_user_id: uuid.UUID) -> dict:
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        'sub': str(test_user_id),
        'email': 'test@example.com',
        'exp': expiry,
        'aud': settings.AUTH_TOKEN_AUDIENCE,
    }
    # Encode the token
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.AUTH_TOKEN_ALGORITHM,
    )

    auth_headers = {'Authorization': f'Bearer {token}'}

    return auth_headers


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_risk_definition_check_insufficient_tokens(
    subject_service, entitlement_service, metering_service, test_user_id, mock_get_entitlement_value
):
    """
    Test that requests are rejected when a user has insufficient tokens.
    """
    # Configure the mock to return an entitlement with insufficient tokens
    mock_get_entitlement_value.return_value = Entitlement(
        feature_key=settings.OPENMETER_FEATURE_KEY,
        has_access=True,
        balance=0,  # No tokens left
        limit=1000,
        usage=1000,
        period='MONTH',
    )

    # Create a request payload
    payload = {
        'business_context': {
            'project_id': 'test-project',
            'project_description': 'Test project description',
            'domain_knowledge': 'Test domain knowledge',
            'language': 'en',
        },
        'risk_description': 'Test risk description',
    }

    # Get auth headers for the test user
    auth_headers = await get_auth_token(test_user_id)

    # Call the risk definition check endpoint
    response = client.post('/api/risk/check/definition/', json=payload, headers=auth_headers)

    # Verify that the request was rejected with a 403 Forbidden status code
    assert response.status_code == 403
    response_data = response.json()
    assert 'detail' in response_data
    assert 'Insufficient token balance' in response_data['detail']

    # Verify that the entitlement service was called to check the token balance
    mock_get_entitlement_value.assert_called_with(
        subject_id=test_user_id, feature_key=settings.OPENMETER_FEATURE_KEY
    )
