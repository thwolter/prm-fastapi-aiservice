from fastapi.testclient import TestClient
from unittest.mock import patch

from app.models import RiskDefinitionCheckResponse
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@patch('app.services.services.RiskDefinitionService.execute_query')
def test_risk_definition_check(mock_execute_query):
    request_data = {
        "text": "The project might face delays due to unforeseen circumstances."
    }
    mock_execute_query.return_value = RiskDefinitionCheckResponse(
        is_valid=True,
        classification="Risk",
        original=request_data["text"],
        suggestion="Consider adding buffer time to the project schedule.",
        explanation="Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk."
    )
    response = client.post("/api/risk-definition/check/", json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(RiskDefinitionCheckResponse(**response_data), RiskDefinitionCheckResponse)
    assert response_data["suggestion"] == "Consider adding buffer time to the project schedule."
    assert response_data["explanation"] == "Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk."