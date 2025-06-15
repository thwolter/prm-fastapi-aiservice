"""Example of mocking riskgpt functions for testing.

This file demonstrates how to mock the search functions and chain.invoke methods
in riskgpt for testing purposes.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient
from riskgpt.models import schemas as rg_schemas
from riskgpt.models.schemas import default_response_info
from riskgpt.utils import search

from src.main import app

client = TestClient(app)


@patch("riskgpt.utils.search.search")
def test_mock_search_function(mock_search):
    """Test mocking the search.search function."""
    # Mock the search function to return a predefined result
    mock_search.return_value = (
        [
            {
                "title": "Mocked Search Result",
                "url": "https://example.com",
                "date": "",
                "type": "web",
                "comment": "This is a mocked search result",
            }
        ],
        True,
    )

    # Now any call to search.search will return the mocked result
    results, success = search.search("test query", "web")

    assert success is True
    assert len(results) == 1
    assert results[0]["title"] == "Mocked Search Result"


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_mock_chain_invoke(mock_execute_query):
    """Test mocking the service execute_query method."""
    # Mock the execute_query method to return a predefined result
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(
                title="Mocked Risk", description="This is a mocked risk", category="Test"
            ),
        ],
        references=["Mocked Reference"],
        response_info=default_response_info(),
    )

    # Create a request payload
    payload = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
            "domain_knowledge": "Test domain knowledge",
            "language": "en",
        },
        "category": "Test",
        "max_risks": 5,
        "existing_risks": [],
    }

    # Call the risk identification endpoint
    response = client.post("/api/risk/identify/", json=payload)

    # Check that the response is successful
    assert (
        response.status_code == 200
    ), f"Expected 200 OK but got {response.status_code}. Body: {response.json()}"

    # Check that the response has the expected structure
    data = response.json()
    assert "risks" in data
    assert isinstance(data["risks"], list)
    assert len(data["risks"]) == 1
    assert data["risks"][0]["title"] == "Mocked Risk"


@patch("riskgpt.utils.search._google_search")
def test_mock_specific_search_function(mock_google_search):
    """Test mocking a specific search function."""
    # Mock the _google_search function to return a predefined result
    mock_google_search.return_value = (
        [
            {
                "title": "Mocked Google Search Result",
                "url": "https://example.com",
                "date": "",
                "type": "web",
                "comment": "This is a mocked Google search result",
            }
        ],
        True,
    )

    # Mock the search function directly to use our mocked _google_search
    with patch(
        "riskgpt.utils.search.search",
        side_effect=lambda query, source_type: mock_google_search(query, source_type),
    ):
        # Now any call to search.search will use our mocked _google_search
        results, success = search.search("test query", "web")

        assert success is True
        assert len(results) == 1
        assert results[0]["title"] == "Mocked Google Search Result"


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_mock_specific_chain_invoke(mock_execute_query):
    """Test mocking a specific service's execute_query method."""
    # Mock the execute_query method to return a predefined result
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(
                title="Specific Mocked Risk",
                description="This is a specifically mocked risk",
                category="Test",
            ),
        ],
        references=["Specific Mocked Reference"],
        response_info=default_response_info(),
    )

    # Create a request payload
    payload = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
            "domain_knowledge": "Test domain knowledge",
            "language": "en",
        },
        "category": "Test",
        "max_risks": 5,
        "existing_risks": [],
    }

    # Call the risk identification endpoint
    response = client.post("/api/risk/identify/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "risks" in data
    assert isinstance(data["risks"], list)
    assert len(data["risks"]) == 1
    assert data["risks"][0]["title"] == "Specific Mocked Risk"
