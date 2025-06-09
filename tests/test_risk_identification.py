import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_risk_identification_endpoint():
    """Test that the risk identification endpoint works correctly."""
    payload = {
        "project_id": "string",
        "project_description": "Glasfaserkabel vermakrtung und operation",
        "category": "Market Risk",
        "max_risks": 5,
        "domain_knowledge": "string",
        "existing_risks": ["string"],
        "language": "en"
    }
    
    response = client.post("/api/risk/identify/", json=payload)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response has the expected structure
    data = response.json()
    assert "success" in data
    assert data["success"] is True
    assert "risks" in data
    assert isinstance(data["risks"], list)