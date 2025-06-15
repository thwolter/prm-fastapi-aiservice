from unittest.mock import patch

from fastapi.testclient import TestClient
from riskgpt.models import schemas as rg_schemas
from riskgpt.models.schemas import default_response_info

from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskMonitoringService.execute_query")
def test_risk_monitoring_endpoint(mock_execute_query):
    """Test that the risk monitoring endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.MonitoringResponse(
        indicators=[
            "Daily backup success rate",
            "System response time",
            "Number of failed migration attempts",
            "Data integrity checks",
        ],
        references=["Industry best practices", "Previous project metrics"],
        response_info=default_response_info(),
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risk_description": "Risk of data loss during migration",
    }

    response = client.post("/api/risk/monitoring/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "indicators" in data
    assert isinstance(data["indicators"], list)
    assert len(data["indicators"]) == 4
    assert "Daily backup success rate" in data["indicators"]
    assert "System response time" in data["indicators"]
    assert "references" in data
    assert isinstance(data["references"], list)
    assert len(data["references"]) == 2


@patch("src.services.services.RiskMonitoringService.execute_query")
def test_risk_monitoring_minimal_description(mock_execute_query):
    """Test risk monitoring with minimal risk description."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.MonitoringResponse(
        indicators=["Project milestone completion rate", "Budget variance"],
        references=None,
        response_info=default_response_info(),
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration",
            "language": "en",
        },
        "risk_description": "Project failure",
    }

    response = client.post("/api/risk/monitoring/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "indicators" in data
    assert isinstance(data["indicators"], list)
    assert len(data["indicators"]) == 2
    assert "Project milestone completion rate" in data["indicators"]
    assert "Budget variance" in data["indicators"]
    assert "references" in data
    assert data["references"] is None
