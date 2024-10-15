from fastapi.testclient import TestClient

from app.router import RiskDefinitionCheckResponse
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_risk_definition_check():
    request_data = {
        "text": "The project might face delays due to unforeseen circumstances."
    }
    response = client.post("/api/risk-definition/check/", json=request_data)
    assert response.status_code == 200
    assert isinstance(RiskDefinitionCheckResponse(**response.json()), RiskDefinitionCheckResponse)