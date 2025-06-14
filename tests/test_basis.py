import pytest


def test_root(client):
    response = client.get("/api/_health")
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.integration
def test_health_check_returns_ok(client):
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
