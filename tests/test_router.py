import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_check_risk_definition():
    response = client.post("/api/check/risk-definition/")
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}