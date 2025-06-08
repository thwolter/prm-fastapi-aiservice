import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.context.schemas import ContextQualityRequest, ContextQualityResponse


@pytest.fixture(scope='function')
def quality_request_data():
    return ContextQualityRequest(
        project_name='Example Project',
        project_context='A short context',
    ).model_dump()


@patch('src.context.service.ContextQualityService.execute_query')
def test_context_quality_valid_input(mock_execute_query, test_client, quality_request_data):
    mock_execute_query.return_value = ContextQualityResponse(
        quality_score=0.9,
        rationale='Looks good',
        tokens_info={},
    )
    response = test_client.post('/api/context/check/', json=quality_request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert response_data['quality_score'] == 0.9
    assert response_data['rationale'] == 'Looks good'


@pytest.mark.webtest
def test_live_context_quality_valid_input(quality_request_data):
    with TestClient(app) as client:
        response = client.post('/api/context/check/', json=quality_request_data)
        assert response.status_code == 200
        print(json.dumps(response.json(), indent=4))
