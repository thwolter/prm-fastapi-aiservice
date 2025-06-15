from unittest.mock import patch

from fastapi.testclient import TestClient
from riskgpt.models import schemas as rg_schemas
from riskgpt.models.schemas import default_response_info

from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskBiasCheckService.execute_query")
def test_risk_bias_check_endpoint(mock_execute_query):
    """Test that the risk bias check endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.BiasCheckResponse(
        biases=["Ambiguity bias", "Confirmation bias", "Availability bias"],
        suggestions="Be more specific about the risk probability and impact. Consider data from multiple sources.",
        response_info=default_response_info(),
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "risk_description": "The project might fail due to technical issues.",
    }

    response = client.post("/api/risk/check/bias/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "biases" in data
    assert isinstance(data["biases"], list)
    assert len(data["biases"]) == 3
    assert "Ambiguity bias" in data["biases"]
    assert "Confirmation bias" in data["biases"]
    assert "Availability bias" in data["biases"]
    assert (
        data["suggestions"]
        == "Be more specific about the risk probability and impact. Consider data from multiple sources."
    )


@patch("src.services.services.RiskBiasCheckService.execute_query")
def test_risk_bias_check_no_biases(mock_execute_query):
    """Test risk bias check with no biases found."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.BiasCheckResponse(
        biases=[],
        suggestions="No biases detected. The risk description is well-formulated.",
        response_info=default_response_info(),
    )

    payload = {
        "risk_description": "There is a 30% probability that the cloud migration will experience critical technical failures within the first 3 months of deployment, potentially causing 4 hours of downtime."
    }

    response = client.post("/api/risk/check/bias/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "biases" in data
    assert isinstance(data["biases"], list)
    assert len(data["biases"]) == 0
    assert data["suggestions"] == "No biases detected. The risk description is well-formulated."
