from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskOpportunityService.execute_query")
def test_risk_opportunity_endpoint(mock_execute_query):
    """Test that the risk opportunity endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.OpportunityResponse(
        opportunities=[
            "Opportunity to modernize infrastructure during cloud migration",
            "Chance to implement improved security measures",
            "Potential for cost optimization through cloud resource management",
        ],
        references=["Industry best practices", "Previous project outcomes"],
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

    response = client.post("/api/risk/opportunities/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "opportunities" in data
    assert isinstance(data["opportunities"], list)
    assert len(data["opportunities"]) == 3
    assert "Opportunity to modernize infrastructure during cloud migration" in data["opportunities"]
    assert "references" in data
    assert isinstance(data["references"], list)
    assert len(data["references"]) == 2


@patch("src.services.services.RiskOpportunityService.execute_query")
def test_risk_opportunity_empty_risks(mock_execute_query):
    """Test risk opportunity with empty risks list."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.OpportunityResponse(
        opportunities=[
            "General opportunity to improve project management practices",
            "Chance to establish better risk assessment processes",
        ],
        references=None,
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration",
            "language": "en",
        },
        "risks": [],
    }

    response = client.post("/api/risk/opportunities/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "opportunities" in data
    assert isinstance(data["opportunities"], list)
    assert len(data["opportunities"]) == 2
    assert "General opportunity to improve project management practices" in data["opportunities"]
    assert "references" in data
    assert data["references"] is None
