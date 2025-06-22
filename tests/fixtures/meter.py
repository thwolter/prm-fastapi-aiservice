import uuid

import pytest
import pytest_asyncio
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.services.metering_service import MeteringService


@pytest_asyncio.fixture
def openmeter_clients():
    """
    Fixture that provides real OpenMeter clients for e2e testing.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    sync_client = Client(endpoint=settings.OPENMETER_API_URL, headers=headers)
    async_client = AsyncClient(endpoint=settings.OPENMETER_API_URL, headers=headers)

    return sync_client, async_client


@pytest.fixture
def test_user_id():
    """
    Fixture that provides a unique user ID for testing.
    """
    return uuid.uuid4()


@pytest_asyncio.fixture
async def metering_service(openmeter_clients, test_user_id, subject_service):
    """
    Fixture that provides a MeteringService instance with a test user.
    """

    yield MeteringService()


class MockMeteringService:
    def __init__(self, has_access_return=True):
        self.has_access_return = has_access_return

    async def check_entitlement(self, subject_id, feature_key=None):
        return {
            'has_access': self.has_access_return,
            'balance': 100 if self.has_access_return else 0,
        }

    async def consume_tokens(self, subject_id, tokens, model=None, prompt=None):
        return True


@pytest.fixture
def mock_metering_service(monkeypatch, has_access_return=True):
    mock_service = MockMeteringService(has_access_return)
    monkeypatch.setattr('src.api.dependencies.get_metering_service', lambda: mock_service)
    return mock_service
