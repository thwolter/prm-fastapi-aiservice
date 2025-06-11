import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root():
    response = client.get("/api/_health")
    assert response.status_code == 204


@pytest.mark.webtest
@pytest.mark.tryfirst
def test_cors_headers_are_present():
    response = client.options("/api/keywords/extract/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-methods" in response.headers
    assert "OPTIONS" in response.headers["access-control-allow-methods"]
    assert "POST" in response.headers["access-control-allow-methods"]


@pytest.mark.webtest
def test_health_check_returns_ok():
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
