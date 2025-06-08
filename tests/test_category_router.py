from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.category.schemas import (
    BaseProjectRequest,
    AddCategoriesRequest,
    IdentifiedCategory,
    CategoriesResponse,
)
from src.project.schemas import Project
from src.main import app


@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        project=Project(
            name='H2 Project',
            context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
        )
    ).model_dump()


@patch('src.category.service.AddRiskCategoriesService.execute_query')
def test_category_identification(mock_execute_query, test_client):
    data = AddCategoriesRequest(
        project=Project(
            name='Removal of a wasp nest.',
            context='Removal of a wasp nest by a service company within the next week.',
        ),
        categories=[],
        type='risk',
    )
    mock_execute_query.return_value = CategoriesResponse(
        categories=[
            IdentifiedCategory(
                name='Sample',
                description='A sample category.',
                examples=['Example 1', 'Example 2'],
                confidence=0.95,
                subcategories=[],
            ),
            IdentifiedCategory(
                name='Text',
                description='A text category.',
                examples=['Example 3', 'Example 4'],
                confidence=0.85,
                subcategories=[],
            ),
        ],
        tokens_info={},
    )
    response = test_client.post('/api/categories/risk/add/', json=data.model_dump())
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(
        CategoriesResponse(**response_data),
        CategoriesResponse,
    )
    assert len(response_data['categories']) == 2
    assert response_data['categories'][0]['name'] == 'Sample'
