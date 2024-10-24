from unittest import skip

from fastapi.testclient import TestClient

from app.main import app
import requests

client = TestClient(app)


@skip
def test_cors_headers_are_present():
    response = client.options('/api/keywords/extract/', headers={'Origin': 'http://localhost:3000'})
    assert response.status_code == 200
    assert 'access-control-allow-origin' in response.headers
    assert response.headers['access-control-allow-origin'] == 'http://localhost:3000'
    assert 'access-control-allow-methods' in response.headers
    assert 'POST' in response.headers['access-control-allow-methods']


def test_health_check_returns_ok():
    response = client.get('/health-check')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openai_connection_successful():
    response = client.get('/health-check/openai/check-connection')
    assert response.status_code == 200
    assert response.json() == {"message": "OpenAI connection successful"}


def test_smith_connection_successful():
    response = client.get('/health-check/smith/check-connection')
    assert response.status_code == 200
    assert response.json() == {"message": "Smith connection successful"}
