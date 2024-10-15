from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_risk_definition_check():
    response = client.post("/api/risk-definition/check/")
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}
