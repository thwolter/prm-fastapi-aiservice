import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.project.schemas import (
    BaseProjectRequest,
    CheckProjectContextResponse,
    ProjectSummaryResponse,
    Project,
)



@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        project=Project(
            name='H2 Project',
            context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
        )
    ).model_dump()


@patch('src.project.service.CheckProjectContextService.execute_query')
def test_check_project_context_valid_input(mock_execute_query, test_client):
    request_data = BaseProjectRequest(
        project=Project(
            name='Project Alpha',
            context='This is a valid project context.',
        )
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
        tokens_info={},
    )
    response = test_client.post('/api/project/check/context/', json=request_data)
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


@patch('src.project.service.ProjectSummaryService.execute_query')
def test_summarize_project_valid_input(mock_execute_query, test_client, project_request_data):
    mock_execute_query.return_value = ProjectSummaryResponse(
        summary='This is a summary of Project Alpha.',
        picture_url='https://example.com/project-alpha.jpg',
        tags=['Alpha', 'Project', 'Summary'],
        image_url='https://example.com/project-alpha.jpg',
        tokens_info={},
    )
    response = test_client.post('/api/project/summarize/', json=project_request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['summary'] == 'This is a summary of Project Alpha.'


@pytest.mark.webtest
def test_live_summarize_project_valid_input(project_request_data):
    response = client.post('/api/project/summarize/', json=project_request_data)
    assert response.status_code == 200
    print(json.dumps(response.json(), indent=4))
