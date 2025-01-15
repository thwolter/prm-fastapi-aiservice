from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.category.schemas import (BaseProjectRequest,
                                  AddCategoriesRequest,
                                  IdentifiedCategory)
from app.main import app

client = TestClient(app)


@pytest.fixture(scope='function')
def project_request_data():
    return BaseProjectRequest(
        name='H2 Project',
        context='Building a H2 cavern at an existing salt cavern site in the Netherlands. The budget is 100M EUR.',
    ).model_dump()


@patch('app.category.service.CategoryIdentificationService.execute_query')
def test_category_identification(mock_execute_query):
    data = BaseProjectRequest(
        name='Removal of a wasp nest.',
        context='Removal of a wasp nest by a service company within the next week.',
    )
    mock_execute_query.return_value = AddCategoriesRequest(
        risks=[
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
        opportunities=[
            IdentifiedCategory(
                name='Sample',
                description='A sample category.',
                examples=['Example 1', 'Example 2'],
                confidence=0.90,
                subcategories=[],
            )
        ],
        impact=[
            IdentifiedCategory(
                name='Sample',
                description='A sample category.',
                examples=['Example 1', 'Example 2'],
                confidence=0.88,
                subcategories=[],
            )
        ],
    )
    response = client.post('/api/categories/create/', json=data.model_dump())
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(
        CategoriesIdentificationResponse(**response_data),
        CategoriesIdentificationResponse,
    )
    assert len(response_data['risks']) == 2
    assert response_data['risks'][0]['name'] == 'Sample'
    assert response_data['impact'][0]['name'] == 'Sample'
