import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def pytest_addoption(parser):
    parser.addoption(
        '--webtest', action='store_true', default=False, help='run tests marked as webtest'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--webtest'):
        return
    skip_webtest = pytest.mark.skip(reason='need --webtest option to run')
    for item in items:
        if 'webtest' in item.keywords:
            item.add_marker(skip_webtest)


@pytest.fixture(scope='session', autouse=True)
def load_env():
    settings.from_env()
    assert settings.OPENAI_API_KEY, 'OPENAI_API_KEY is not set'
    assert settings.LANGCHAIN_API_KEY, 'LANGCHAIN_API_KEY is not set'


@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for testing"""
    original_redis_url = settings.REDIS_URL
    settings.REDIS_URL = 'redis://localhost:6379'
    yield
    settings.REDIS_URL = original_redis_url


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client
