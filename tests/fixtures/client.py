from fastapi.testclient import TestClient
import pytest

from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.cookies.set('auth', 'test')
        yield c


@pytest.fixture
def test_client(client, override_auth):
    yield client
