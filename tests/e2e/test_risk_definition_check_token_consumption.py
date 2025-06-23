"""
Integration tests for RiskDefinitionCheckService with token consumption.
"""

from datetime import datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from azure.core.exceptions import ResourceExistsError
from openmeter.aio import Client
from riskgpt.models.schemas import DefinitionCheckResponse, ResponseInfo

from src.core.config import settings


@pytest.fixture
def riskgpt_payload():
    return {
        'business_context': {
            'project_id': 'test-project',
            'project_description': 'Test project description',
            'domain_knowledge': 'Test domain knowledge',
            'language': 'en',
        },
        'risk_description': 'Test risk description',
    }


@pytest_asyncio.fixture
async def metering_client():
    """
    Fixture to create an OpenMeter client for testing purposes.
    """
    client = Client(endpoint=settings.OPENMETER_LOCAL_API_URL)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def meter(metering_client):
    """
    Fixture to create a meter for testing purposes.
    """
    meter_payload = {
        'name': 'ai_tokens',
        'slug': 'ai_tokens',
        'description': 'LLM tokens',
        'eventType': 'tokens',
        'valueProperty': '$.tokens',
        'aggregation': 'SUM',
        'groupBy': {
            'model': '$.model',
            'prompt': '$.prompt',
        },
        'metadata': None,
    }
    try:
        created_meter = await metering_client.create_meter(meter_payload)
        assert created_meter is not None, 'Meter creation failed'
    except ResourceExistsError:
        created_meter = await metering_client.get_meter(meter_payload['slug'])

    yield created_meter

    try:
        await metering_client.delete_meter(meter_payload['slug'])
    except ResourceExistsError:
        # If an active feature is present, we cannot delete the entitlement
        pass


@pytest_asyncio.fixture
async def feature(metering_client, meter):
    """
    Fixture to create a feature for testing purposes.
    """
    feature_payload = {
        'key': settings.OPENMETER_FEATURE_KEY,
        'meterSlug': 'ai_tokens',
        'name': 'Ai Tokens',
    }

    try:
        created_feature = await metering_client.create_feature(feature_payload)
        assert created_feature is not None, 'Feature creation failed'
    except ResourceExistsError:
        created_feature = await metering_client.get_feature(feature_payload['key'])
    yield created_feature
    metering_client.delete_feature(feature_payload['key'])


@pytest_asyncio.fixture
async def subject(metering_client):
    """
    Fixture to create a subject for testing purposes.
    """
    subject_payload = {
        'key': 'user_001',
        'displayname': 'Test User',
    }

    created_subject = await metering_client.upsert_subject([subject_payload])
    assert created_subject is not None, 'Subject creation failed'
    yield created_subject[0]
    metering_client.delete_subject(created_subject[0]['id'])


@pytest_asyncio.fixture
async def entitlement(metering_client, subject, feature, issue_after_reset=10000):
    """
    Fixture to create an entitlement for a user for testing purposes.
    """
    entitlement_payload = {
        'subjectKey': 'user_001',
        'featureKey': settings.OPENMETER_FEATURE_KEY,
        'issueAfterReset': issue_after_reset,
        'type': 'metered',
        'usagePeriod': {'interval': 'MONTH', 'startDay': 1},
    }

    created_entitlement = await metering_client.create_entitlement(
        subject['key'], entitlement_payload
    )
    if created_entitlement.get('title') == 'Conflict':
        entitlement_id = created_entitlement['extensions']['conflictingEntityId']
        created_entitlement = await metering_client.get_entitlement(subject['key'], entitlement_id)
    assert created_entitlement is not None, 'Entitlement creation failed'

    yield created_entitlement

    try:
        await metering_client.delete_entitlement(subject['id'], created_entitlement['id'])
    except ResourceExistsError:
        # If an active feature is present, we cannot delete the entitlement
        pass


@pytest_asyncio.fixture
async def auth_headers(subject):
    """
    Fixture to create authentication headers for the test user.
    This simulates the process of generating an auth token for the user.
    """
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        'sub': subject['key'],
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


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
async def test_risk_definition_check_sufficient_tokens(
    configure_mock_handle,
    test_client,
    entitlement,
    auth_headers,
    riskgpt_payload,
):
    """
    Test that RiskDefinitionCheckService correctly consumes tokens when a user has sufficient tokens.
    """
    # Configure the mock to return a response with consumed tokens
    consumed_tokens = 50
    mock_response = create_mock_definition_response(consumed_tokens)
    configure_mock_handle(return_value=mock_response)

    # Call the risk definition check endpoint
    response = test_client.post(
        '/api/risk/check/definition/', json=riskgpt_payload, headers=auth_headers
    )
    assert response is not None
    response_data = response.json()

    # Verify the response
    assert response_data is not None
    assert 'revised_description' in response_data
    assert response_data['revised_description'] == 'Text for token consumption testing.'
    assert 'response_info' in response_data
    assert response_data['response_info']['consumed_tokens'] == consumed_tokens


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.usefixtures('e2e_environment')
@pytest.mark.parametrize('entitlement', [0])
async def test_risk_definition_check_insufficient_tokens(
    configure_mock_handle,
    test_client,
    entitlement,
    auth_headers,
    riskgpt_payload,
):
    """
    Test that requests are rejected when a user has insufficient tokens.
    """

    # Configure the mock to return a response with consumed tokens
    consumed_tokens = 50
    mock_response = create_mock_definition_response(consumed_tokens)
    configure_mock_handle(return_value=mock_response)

    # Call the risk definition check endpoint
    response = test_client.post(
        '/api/risk/check/definition/', json=riskgpt_payload, headers=auth_headers
    )
    assert response is not None
    response_data = response.json()

    # Verify that the request was rejected with a 403 Forbidden status code
    assert response.status_code == 403
    response_data = response.json()
    assert 'detail' in response_data
    assert 'Insufficient token entitlement' in response_data['detail']
