from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.models import (CategoriesIdentificationRequest,
                                 CategoriesIdentificationResponse, Category,
                                 RiskDefinitionCheckResponse)

client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello World'}


@patch('app.services.services.RiskDefinitionService.execute_query')
def test_risk_definition_check_valid_input(mock_execute_query):
    request_data = {'text': 'The project might face delays due to unforeseen circumstances.'}
    mock_execute_query.return_value = RiskDefinitionCheckResponse(
        is_valid=True,
        classification='Risk',
        original=request_data['text'],
        suggestion='Consider adding buffer time to the project schedule.',
        explanation='Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk.',
    )
    response = client.post('/api/risk-definition/check/', json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskDefinitionCheckResponse(**response_data), RiskDefinitionCheckResponse)
    assert response_data['suggestion'] == 'Consider adding buffer time to the project schedule.'
    assert (
        response_data['explanation']
        == 'Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk.'
    )


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


@patch('app.services.services.CategoryIdentificationService.execute_query')
def test_category_identification(mock_execute_query):
    data = CategoriesIdentificationRequest(text='This is a sample text to identify categories.')
    mock_execute_query.return_value = CategoriesIdentificationResponse(
        categories=[
            Category(
                name='Sample',
                description='A sample category.',
                examples=['Example 1', 'Example 2'],
            ),
            Category(
                name='Text',
                description='A text category.',
                examples=['Example 3', 'Example 4'],
            ),
        ]
    )
    response = client.post('/api/categories/identify/', json=data.model_dump())
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(
        CategoriesIdentificationResponse(**response_data),
        CategoriesIdentificationResponse,
    )
    assert len(response_data['categories']) == 2
    assert response_data['categories'][0]['name'] == 'Sample'
    assert response_data['categories'][1]['name'] == 'Text'
