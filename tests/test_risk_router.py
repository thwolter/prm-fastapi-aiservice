import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from app.risk.schemas import (
    RiskDriversResponse,
    RiskImpactResponse,
    RiskLikelihoodResponse,
    RiskMitigationResponse,
)

from app.category.schemas import Category
from app.main import app
from app.project.schemas import BaseProjectRequest, Project
from app.risk.schemas import (Risk, RiskDefinitionCheckResponse,
                              RiskDriversRequest, RiskIdentificationRequest,
                              RiskIdentificationResponse)



@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        project=Project(
            name='H2 Project',
            context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
        )
    ).model_dump()


@patch('app.risk.service.RiskDefinitionService.execute_query')
def test_risk_definition_check_valid_input(mock_execute_query, test_client):
    request_data = {'text': 'The project might face delays due to unforeseen circumstances.'}
    mock_execute_query.return_value = RiskDefinitionCheckResponse(
        is_valid=True,
        classification='Risk',
        original=request_data['text'],
        suggestion='Consider adding buffer time to the project schedule.',
        explanation='Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk.',
        tokens_info={},
    )
    response = test_client.post('/api/risk/check/definition/', json=request_data)
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
def test_Live_risk_definition_check_valid_input(test_client):
    request_data = {'text': 'The project might face delays due to unforeseen circumstances.'}
    response = test_client.post('/api/risk/check/definition/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(RiskDefinitionCheckResponse(**response_data), RiskDefinitionCheckResponse)


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_missing_text(mock_execute_query, test_client):
    request_data = {}
    response = test_client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_empty_text(mock_execute_query, test_client):
    request_data = {'text': ''}
    response = test_client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422


@patch('app.services.services.RiskDefinitionService.execute_query')
def risk_definition_check_invalid_text_type(mock_execute_query, test_client):
    request_data = {'text': 12345}
    response = test_client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 422


@pytest.fixture(scope='function')
def risk_identification_request_data():
    return RiskIdentificationRequest(
        project=Project(
            name='Going out for dinner.',
            context='Going out for dinner with friends at a local restaurant.',
        ),
        category=Category(
            name='Operational',
            description='Challenges in securing a reservation at the desired restaurant.',
            examples=['Fully booked restaurants.', 'Limited seating capacity.'],
        ),
        risks=[
            {'title': 'Risk 1', 'description': 'Description of Risk 1'},
            {'title': 'Risk 2', 'description': 'Description of Risk 2'},
        ],
    ).model_dump()


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_valid_input(mock_execute_query, test_client, risk_identification_request_data):
    mock_execute_query.return_value = RiskIdentificationResponse(
        risks=[
            Risk(title='Identified Risk 1', description='Description of Identified Risk 1'),
            Risk(title='Identified Risk 2', description='Description of Identified Risk 2'),
        ],
        tokens_info={},
    )
    response = test_client.post('/api/risk/identify/', json=risk_identification_request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)
    assert len(response_data['risks']) == 2
    assert response_data['risks'][0]['title'] == 'Identified Risk 1'


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_missing_category(mock_execute_query, test_client):
    request_data = {'risks': [{'title': 'Risk 1', 'description': 'Description of Risk 1'}]}
    response = test_client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 422


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_empty_existing(mock_execute_query, test_client, risk_identification_request_data):
    mock_execute_query.return_value = RiskIdentificationResponse(
        risks=[
            Risk(title='Identified Risk 1', description='Description of Identified Risk 1'),
            Risk(title='Identified Risk 2', description='Description of Identified Risk 2'),
        ],
        tokens_info={},
    )
    request_data = risk_identification_request_data
    request_data['risks'] = []
    response = test_client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)


@patch('app.risk.service.RiskIdentificationService.execute_query')
def test_risk_identification_invalid_existing_type(mock_execute_query, test_client):
    request_data = {'category': 'Operational', 'risks': 'invalid_type'}
    response = test_client.post('/api/risk/identify/', json=request_data)
    assert response.status_code == 422


@pytest.mark.webtest
def test_live_risk_identification_valid_input():
    category = Category(
        name='Reservation Availability',
        description='Challenges in securing a reservation at the desired restaurant.',
        examples=['Fully booked restaurants.', 'Limited seating capacity.'],
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
        examples=['Fully booked restaurants.', 'Limited seating capacity.'],
    )
    risk1 = Risk(
        title='Last-Minute Cancellations',
        description='Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.',
    )
    request_data = RiskIdentificationRequest(
        name='Going our for dinner.',
        context='Going out for dinner with friends at a local restaurant.',
        category=category.model_dump(),
        existing=[risk1.model_dump()],
    )
    response = client.post('/api/risk/identify/', json=request_data.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(RiskIdentificationResponse(**response_data), RiskIdentificationResponse)


@pytest.mark.webtest
def test_live_risk_drivers(project_request_data):
    request_data = RiskDriversRequest(
        name='Going our for dinner.',
        context='Going out for dinner with friends at a local restaurant.',
        risk=Risk(
            title='Last-Minute Cancellations',
            description='Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.',
        ).model_dump(),
    )
    response = client.post('/api/risk/drivers/', json=request_data.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    print(json.dumps(response_data, indent=2))
    assert isinstance(RiskDriversResponse(**response_data), RiskDriversResponse)


@pytest.mark.webtest
def test_live_risk_likelihood(project_request_data):
    request_data = {
        'name': 'Going out for dinner.',
        'context': 'Going out for dinner with friends at a local restaurant.',
        'risk': {
            'title': 'Last-Minute Cancellations',
            'description': 'Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.',
        },
        'drivers': ['Last-Minute Cancellations'],
    }
    response = client.post('/api/risk/likelihood/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    print(json.dumps(response_data, indent=2))
    assert isinstance(RiskLikelihoodResponse(**response_data), RiskLikelihoodResponse)


@pytest.mark.webtest
def test_live_risk_impact(project_request_data):
    request_data = {
        'name': 'Going out for dinner.',
        'context': 'Going out for dinner with friends at a local restaurant.',
        'risk': {
            'title': 'Last-Minute Cancellations',
            'description': 'Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.',
        },
        'drivers': ['Last-Minute Cancellations'],
    }
    response = client.post('/api/risk/impact/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    print(json.dumps(response_data, indent=2))
    assert isinstance(RiskImpactResponse(**response_data), RiskImpactResponse)


@pytest.mark.webtest
def test_live_risk_mitigation(project_request_data):
    request_data = {
        'name': 'Going out for dinner.',
        'context': 'Going out for dinner with friends at a local restaurant.',
        'risk': {
            'title': 'Last-Minute Cancellations',
            'description': 'Friends or diners canceling their reservations unexpectedly, leading to less availability for the group.',
        },
        'drivers': ['Last-Minute Cancellations'],
    }
    response = client.post('/api/risk/mitigation/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    print(json.dumps(response_data, indent=2))
    assert isinstance(RiskMitigationResponse(**response_data), RiskMitigationResponse)
