from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient  # noqa: F401

from src.category.riskgpt_service import (
    CategoryRequest,
    CategoryResponse,
    RiskGPTCategoryService,
)
from src.main import app


@patch('src.category.riskgpt_service.RiskGPTCategoryService.execute_query')
def test_category_identification(mock_execute_query, test_client):
    data = CategoryRequest(
        project_id='1',
        project_description='Removal of a wasp nest by a service company within the next week.',
    )
    mock_execute_query.return_value = CategoryResponse(
        categories=['Sample', 'Text'],
        rationale='demo',
        response_info=None,
    )
    response = test_client.post('/api/categories/', json=data.model_dump())
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert CategoryResponse(**response_data)
    assert len(response_data['categories']) == 2
    assert response_data['categories'][0] == 'Sample'
