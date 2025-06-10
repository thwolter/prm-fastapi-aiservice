import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)

@patch('src.services.services.RiskIdentificationService.execute_query')
def test_risk_identification_endpoint(mock_execute_query):
    """Test that the risk identification endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(title="Market Risk 1", description="Description of Market Risk 1", category="Market Risk"),
            rg_schemas.Risk(title="Market Risk 2", description="Description of Market Risk 2", category="Market Risk"),
        ],
        references=["Mock Reference"],
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Glasfaserkabel vermarktung und operation",
            "domain_knowledge": "string",
            "language": "en"
        },
        "category": "Market Risk",
        "max_risks": 5,
        "existing_risks": ["string"]
    }

    response = client.post("/api/risk/identify/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "risks" in data
    assert isinstance(data["risks"], list)
    assert len(data["risks"]) == 2
    assert data["risks"][0]["title"] == "Market Risk 1"
    assert data["risks"][1]["title"] == "Market Risk 2"

@patch('src.services.services.RiskIdentificationService.execute_query')
def test_risk_identification_with_mock(mock_execute_query):
    """Test risk identification with mocked service response."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(title="Risk 1", description="Description of Risk 1", category="Market Risk"),
            rg_schemas.Risk(title="Risk 2", description="Description of Risk 2", category="Market Risk"),
        ],
        references=None,
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Glasfaserkabel vermarktung und operation",
            "domain_knowledge": "string",
            "language": "en"
        },
        "category": "Market Risk",
        "max_risks": 5,
        "existing_risks": ["string"]
    }

    response = client.post("/api/risk/identify/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "risks" in data
    assert isinstance(data["risks"], list)
    assert len(data["risks"]) == 2
    assert data["risks"][0]["title"] == "Risk 1"
    assert data["risks"][1]["title"] == "Risk 2"
