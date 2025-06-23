"""
Integration tests for RiskDefinitionCheckService with token consumption.
"""

import pytest
from riskgpt.models.schemas import DefinitionCheckResponse, ResponseInfo


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


@pytest.mark.openmeter
@pytest.mark.asyncio
async def test_risk_definition_check_sufficient_tokens(
    configure_mock_handle,
    test_client,
    local_entitlement_for_tokens,
    local_auth_headers,
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
        '/api/risk/check/definition/', json=riskgpt_payload, headers=local_auth_headers
    )
    assert response is not None
    response_data = response.json()

    # Verify the response
    assert response_data is not None
    assert 'revised_description' in response_data
    assert response_data['revised_description'] == 'Text for token consumption testing.'
    assert 'response_info' in response_data
    assert response_data['response_info']['consumed_tokens'] == consumed_tokens


@pytest.mark.openmeter
@pytest.mark.asyncio
@pytest.mark.parametrize('local_entitlement_for_tokens', [0])
async def test_risk_definition_check_insufficient_tokens(
    configure_mock_handle,
    test_client,
    local_entitlement_for_tokens,
    local_auth_headers,
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
        '/api/risk/check/definition/', json=riskgpt_payload, headers=local_auth_headers
    )

    # Verify that the request was rejected with a 403 Forbidden status code
    assert response.status_code == 403
    response_data = response.json()
    assert 'detail' in response_data
    assert 'Insufficient token entitlement' in response_data['detail']
