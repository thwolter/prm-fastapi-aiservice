from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskCorrelationTagsService.execute_query")
def test_risk_correlation_tags_endpoint(mock_execute_query):
    """Test that the risk correlation tags endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CorrelationTagResponse(
        tags=[
            "technical_infrastructure",
            "data_integrity",
            "service_availability",
            "cost_management",
        ],
        rationale="These tags represent common factors that could influence multiple risks in the cloud migration project.",
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risk_titles": [
            "Data Loss During Migration",
            "Service Interruption",
            "Cost Overruns",
            "Security Vulnerabilities",
        ],
        "known_drivers": [
            "Inadequate testing",
            "Network instability",
            "Inaccurate resource estimation",
        ],
    }

    response = client.post("/api/risk/correlation-tags/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) == 4
    assert "technical_infrastructure" in data["tags"]
    assert "data_integrity" in data["tags"]
    assert "rationale" in data
    assert isinstance(data["rationale"], str)
    assert len(data["rationale"]) > 0


@patch("src.services.services.RiskCorrelationTagsService.execute_query")
def test_risk_correlation_tags_no_drivers(mock_execute_query):
    """Test risk correlation tags with no known drivers."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CorrelationTagResponse(
        tags=["project_management", "technical_implementation"],
        rationale="Basic tags derived from risk titles only.",
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration",
            "language": "en",
        },
        "risk_titles": ["Project Delay", "Technical Failure"],
    }

    response = client.post("/api/risk/correlation-tags/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) == 2
    assert "project_management" in data["tags"]
    assert "technical_implementation" in data["tags"]
    assert "rationale" in data
    assert isinstance(data["rationale"], str)
    assert len(data["rationale"]) > 0
