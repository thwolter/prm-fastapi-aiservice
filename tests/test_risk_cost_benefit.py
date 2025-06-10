from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskCostBenefitService.execute_query")
def test_risk_cost_benefit_endpoint(mock_execute_query):
    """Test that the risk cost-benefit endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CostBenefitResponse(
        analyses=[
            rg_schemas.CostBenefit(
                mitigation="Implement backup solution",
                cost="High initial investment, moderate ongoing costs",
                benefit="Prevents data loss, enables quick recovery",
            ),
            rg_schemas.CostBenefit(
                mitigation="Staff training",
                cost="Moderate one-time cost",
                benefit="Reduces human error, improves response time",
            ),
        ],
        references=["Industry best practices", "Previous project lessons"],
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risk_description": "Risk of data loss during migration",
        "mitigations": ["Implement backup solution", "Staff training"],
    }

    response = client.post("/api/risk/cost-benefit/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "analyses" in data
    assert isinstance(data["analyses"], list)
    assert len(data["analyses"]) == 2
    assert data["analyses"][0]["mitigation"] == "Implement backup solution"
    assert data["analyses"][1]["mitigation"] == "Staff training"
    assert "references" in data
    assert isinstance(data["references"], list)
    assert len(data["references"]) == 2


@patch("src.services.services.RiskCostBenefitService.execute_query")
def test_risk_cost_benefit_empty_mitigations(mock_execute_query):
    """Test risk cost-benefit with empty mitigations list."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CostBenefitResponse(
        analyses=[],
        references=None,
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risk_description": "Risk of data loss during migration",
        "mitigations": [],
    }

    response = client.post("/api/risk/cost-benefit/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "analyses" in data
    assert isinstance(data["analyses"], list)
    assert len(data["analyses"]) == 0
