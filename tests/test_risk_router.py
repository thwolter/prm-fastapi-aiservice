from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.project.schemas import BaseProjectRequest
from app.risk.schemas import RiskDefinitionCheckResponse

client = TestClient(app)


@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        name='H2 Project',
        context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
    ).model_dump()


@patch('app.risk.service.RiskDefinitionService.execute_query')
def test_risk_definition_check_valid_input(mock_execute_query):
    request_data = {'text': 'The project might face delays due to unforeseen circumstances.'}
    mock_execute_query.return_value = RiskDefinitionCheckResponse(
        is_valid=True,
        classification='Risk',
        original=request_data['text'],
        suggestion='Consider adding buffer time to the project schedule.',
        explanation='Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk.',
    )
    response = client.post('/api/risk/check/definition/', json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskDefinitionCheckResponse(**response_data), RiskDefinitionCheckResponse)
    assert response_data['suggestion'] == 'Consider adding buffer time to the project schedule.'
    assert (
        response_data['explanation']
        == 'Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk.'
    )


@pytest.mark.webtest
def test_Live_risk_definition_check_valid_input():
    request_data = {'text': 'The project might face delays due to unforeseen circumstances.'}
    response = client.post('/api/risk/check/definition/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(RiskDefinitionCheckResponse(**response_data), RiskDefinitionCheckResponse)


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_missing_text(mock_execute_query):
    request_data = {}
    response = client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_empty_text(mock_execute_query):
    request_data = {'text': ''}
    response = client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_invalid_text_type(mock_execute_query):
    request_data = {'text': 12345}
    response = client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422
