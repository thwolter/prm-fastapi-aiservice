from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.RiskCommunicationService.execute_query")
def test_risk_communication_endpoint(mock_execute_query):
    """Test that the risk communication endpoint works correctly with mocking."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CommunicationResponse(
        executive_summary="The cloud migration project faces three key risks: data loss, service interruption, and cost overruns. Mitigation strategies have been identified for each risk.",
        technical_annex="Detailed technical analysis of each risk:\n1. Data Loss: ...\n2. Service Interruption: ...\n3. Cost Overruns: ...",
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration project",
            "domain_knowledge": "string",
            "language": "en",
        },
        "summary": "The project involves migrating on-premises infrastructure to the cloud. Key risks include data loss during migration, service interruption, and cost overruns.",
    }

    response = client.post("/api/risk/communicate/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "executive_summary" in data
    assert isinstance(data["executive_summary"], str)
    assert len(data["executive_summary"]) > 0
    assert "technical_annex" in data
    assert isinstance(data["technical_annex"], str)
    assert len(data["technical_annex"]) > 0


@patch("src.services.services.RiskCommunicationService.execute_query")
def test_risk_communication_minimal_summary(mock_execute_query):
    """Test risk communication with minimal summary."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.CommunicationResponse(
        executive_summary="The project has minimal information available. More details are needed for a comprehensive risk assessment.",
        technical_annex=None,
        response_info=None,
    )

    payload = {
        "business_context": {
            "project_id": "string",
            "project_description": "Cloud migration",
            "language": "en",
        },
        "summary": "Cloud migration project.",
    }

    response = client.post("/api/risk/communicate/", json=payload)

    # Check that the response is successful
    assert response.status_code == 200

    # Check that the response has the expected structure
    data = response.json()
    assert "executive_summary" in data
    assert isinstance(data["executive_summary"], str)
    assert len(data["executive_summary"]) > 0
    assert "technical_annex" in data
    assert data["technical_annex"] is None
