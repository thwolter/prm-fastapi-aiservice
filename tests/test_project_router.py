import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.project.schemas import (BaseProjectRequest,
                                 CheckProjectContextResponse,
                                 ProjectSummaryResponse)

client = TestClient(app)


@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        name='H2 Project',
        context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
    ).model_dump()


@patch('app.project.service.CheckProjectContextService.execute_query')
def test_check_project_context_valid_input(mock_execute_query):
    request_data = BaseProjectRequest(
        **{'context': 'This is a valid project context.', 'name': 'Project Alpha'}
    ).model_dump()
    mock_execute_query.return_value = CheckProjectContextResponse(
        is_valid=True,
        name=request_data['name'],
        suggestion='No changes needed.',
        explanation='The project context is well-defined.',
        missing=[],
        context_example='This is a valid project context.',
        language='en',
        capabilities=['Capability 1', 'Capability 2'],
        challenges=['Challenge 1', 'Challenge 2'],
        budget='100M EUR',
        currency='EUR',
        timeline='Q1 2024',
        deadline='2024-03-31',
    )
    response = client.post('/api/project/check/context/', json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert response_data['is_valid'] is True
    assert response_data['suggestion'] == 'No changes needed.'
    assert response_data['explanation'] == 'The project context is well-defined.'
    assert response_data['missing'] == []


@pytest.mark.webtest
def test_live_check_project_context_valid_input(project_request_data):
    with TestClient(app) as client:
        response = client.post('/api/project/check/context/', json=project_request_data)
        assert response.status_code == 200
        print(json.dumps(response.json(), indent=4))


@patch('app.project.service.ProjectSummaryService.execute_query')
def test_summarize_project_valid_input(mock_execute_query, project_request_data):
    mock_execute_query.return_value = ProjectSummaryResponse(
        summary='This is a summary of Project Alpha.',
        picture_url='https://example.com/project-alpha.jpg',
        tags=['Alpha', 'Project', 'Summary'],
        image_url='https://example.com/project-alpha.jpg',
    )
    response = client.post('/api/project/summarize/', json=project_request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['summary'] == 'This is a summary of Project Alpha.'


@pytest.mark.webtest
def test_live_summarize_project_valid_input(project_request_data):
    response = client.post('/api/project/summarize/', json=project_request_data)
    assert response.status_code == 200
    print(json.dumps(response.json(), indent=4))
