import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.project.schemas import BaseProjectRequest
from app.risk.schemas import RiskDefinitionCheckResponse, RiskIdentificationResponse, Risk
from app.category.schemas import Category
from app.risk.schemas import RiskIdentificationRequest

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



@pytest.fixture(scope='function')
def risk_identification_request_data():
    return RiskIdentificationRequest(
        name = 'Going out for dinner.',
        context = 'Going out for dinner with friends at a local restaurant.',
        category = Category(
            name = 'Operational',
            description = 'Challenges in securing a reservation at the desired restaurant.',
            examples = ['Fully booked restaurants.', 'Limited seating capacity.']
        ),
        existing = [
            {'title': 'Risk 1', 'description': 'Description of Risk 1'},
            {'title': 'Risk 2', 'description': 'Description of Risk 2'}
        ]
    ).model_dump()


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_valid_input(mock_execute_query, risk_identification_request_data):
    mock_execute_query.return_value = RiskIdentificationResponse(
        risks=[
            Risk(title='Identified Risk 1', description='Description of Identified Risk 1'),
            Risk(title='Identified Risk 2', description='Description of Identified Risk 2')
        ]
    )
    response = client.post('/api/risk/identify/', json=risk_identification_request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)
    assert len(response_data['risks']) == 2
    assert response_data['risks'][0]['title'] == 'Identified Risk 1'


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_missing_category(mock_execute_query):
    request_data = {'existing': [{'title': 'Risk 1', 'description': 'Description of Risk 1'}]}
    response = client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 422


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_empty_existing(mock_execute_query, risk_identification_request_data):
    mock_execute_query.return_value = RiskIdentificationResponse(
        risks=[
            Risk(title='Identified Risk 1', description='Description of Identified Risk 1'),
            Risk(title='Identified Risk 2', description='Description of Identified Risk 2')
        ]
    )
    request_data = risk_identification_request_data
    request_data['existing'] = []
    response = client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_invalid_existing_type(mock_execute_query):
    request_data = {'category': 'Operational', 'existing': 'invalid_type'}
    response = client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 422



@pytest.mark.webtest
def test_live_risk_identification_valid_input():
    category = Category(
        name='Reservation Availability',
        description='Challenges in securing a reservation at the desired restaurant.',
        examples=['Fully booked restaurants.', 'Limited seating capacity.']
    )
    request_data = RiskIdentificationRequest(
        name='Going our for dinner.',
        context='Going out for dinner with friends at a local restaurant.',
        category=category.model_dump(),
    )
    response = client.post('/api/risk/identify/', json=request_data.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)



@pytest.mark.webtest
def test_live_risk_identification_valid_input_existing_risks():
    category = Category(
        name='Reservation Availability',
        description='Challenges in securing a reservation at the desired restaurant.',
        examples=['Fully booked restaurants.', 'Limited seating capacity.']
    )
    risk1 = Risk(
        title='Last-Minute Cancellations',
        description='Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.'
    )
    request_data = RiskIdentificationRequest(
        name='Going our for dinner.',
        context='Going out for dinner with friends at a local restaurant.',
        category=category.model_dump(),
        existing=[risk1.model_dump()]
    )
    response = client.post('/api/risk/identify/', json=request_data.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)