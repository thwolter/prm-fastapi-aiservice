from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskPrioritizationService.execute_query")
def test_risk_prioritization_endpoint(mock_execute_query):
    """Test that the risk prioritization endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.PrioritizationResponse(
        prioritized_risks=[
            "High Priority Risk 1",
            "Medium Priority Risk 2",
            "Low Priority Risk 3",
        ],
        rationale="Risks were prioritized based on impact and probability.",
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risks": [
            "Risk of data loss during migration",
            "Risk of service interruption",
            "Risk of cost overruns",
        ],
    }

    response = client.post("/api/risk/prioritize/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "prioritized_risks" in data
    assert isinstance(data["prioritized_risks"], list)
    assert len(data["prioritized_risks"]) == 3
    assert data["prioritized_risks"][0] == "High Priority Risk 1"
    assert data["prioritized_risks"][1] == "Medium Priority Risk 2"
    assert data["prioritized_risks"][2] == "Low Priority Risk 3"
    assert data["rationale"] == "Risks were prioritized based on impact and probability."


@patch("src.services.services.RiskPrioritizationService.execute_query")
def test_risk_prioritization_empty_risks(mock_execute_query):
    """Test risk prioritization with empty risks list."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.PrioritizationResponse(
        prioritized_risks=[],
        rationale="No risks to prioritize.",
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risks": [],
    }

    response = client.post("/api/risk/prioritize/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "prioritized_risks" in data
    assert isinstance(data["prioritized_risks"], list)
    assert len(data["prioritized_risks"]) == 0
    assert data["rationale"] == "No risks to prioritize."
