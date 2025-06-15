import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client(auth_headers):
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c


@pytest.fixture
def test_client(client, override_auth):
    yield client
