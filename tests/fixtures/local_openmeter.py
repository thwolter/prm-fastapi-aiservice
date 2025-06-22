import uuid

import pytest
import pytest_asyncio
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.services.metering_service import MeteringService


# Session-scoped fixture for local OpenMeter clients
@pytest_asyncio.fixture(scope='session')
def local_openmeter_clients():
    """
    Fixture that provides OpenMeter clients configured to use the local instance.

    This fixture connects to the local OpenMeter instance running at http://localhost:8888
    as described in the README.md. No authentication is required for the local instance.

    Returns:
        A tuple containing (sync_client, async_client)
    """
    # Local OpenMeter instance URL
    local_endpoint = 'http://localhost:8888'

    # No authentication headers needed for local instance
    headers = {
        'Accept': 'application/json',
    }

    # Create both sync and async clients
    sync_client = Client(endpoint=local_endpoint, headers=headers)
    async_client = AsyncClient(endpoint=local_endpoint, headers=headers)

    return sync_client, async_client


@pytest.fixture
@pytest.mark.integration
def test_subject_id():
    """
    Fixture that provides a unique subject ID for testing.
    """
    return str(uuid.uuid4())


@pytest_asyncio.fixture
async def local_meter(local_openmeter_clients):
    """
    Fixture that creates a meter in the local OpenMeter instance.

    Returns:
        The created meter object
    """
    sync_client, _ = local_openmeter_clients

    # Create a unique meter ID for testing
    meter_id = f'test-meter-{uuid.uuid4()}'

    # Define the meter
    meter = {
        'id': meter_id,
        'display_name': 'Test Meter',
        'description': 'Meter for testing',
        'event_type': settings.OPENMETER_EVENT_TYPE,
        'aggregation': 'sum',
        'unit': 'tokens',
        'value_property': 'tokens',
    }

    # Create the meter
    sync_client.create_meter(meter)

    yield meter_id

    # Clean up after test
    try:
        sync_client.delete_meter(meter_id)
    except Exception as e:
        print(f'Failed to delete meter {meter_id}: {e}')


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_feature(local_openmeter_clients, local_meter):
    """
    Fixture that creates a feature in the local OpenMeter instance.

    Returns:
        The created feature object
    """
    sync_client, _ = local_openmeter_clients

    # Create a unique feature ID for testing
    feature_id = f'test-feature-{uuid.uuid4()}'

    # Define the feature
    feature = {
        'id': feature_id,
        'display_name': 'Test Feature',
        'description': 'Feature for testing',
        'meter_id': local_meter,
        'reset_period': 'MONTH',
    }

    # Create the feature
    sync_client.create_feature(feature)

    yield feature_id

    # Clean up after test
    try:
        sync_client.delete_feature(feature_id)
    except Exception as e:
        print(f'Failed to delete feature {feature_id}: {e}')


@pytest_asyncio.fixture
async def local_entitlement(local_openmeter_clients, local_feature, test_subject_id):
    """
    Fixture that creates an entitlement in the local OpenMeter instance.

    Returns:
        The created entitlement object
    """
    sync_client, _ = local_openmeter_clients

    # Define the entitlement
    entitlement = {
        'subject_id': test_subject_id,
        'feature_id': local_feature,
        'limit': 1000,  # Initial token balance
    }

    # Create the entitlement
    sync_client.create_entitlement(entitlement)

    yield entitlement

    # Clean up after test
    try:
        sync_client.delete_entitlement(test_subject_id, local_feature)
    except Exception as e:
        print(
            f'Failed to delete entitlement for subject {test_subject_id}, feature {local_feature}: {e}'
        )


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_metering_service(
    local_openmeter_clients, local_feature, local_entitlement, test_subject_id
):
    """
    Fixture that provides a MeteringService instance configured to use the local OpenMeter instance.

    This fixture overrides the default MeteringService configuration to use the local OpenMeter instance.
    It also ensures a meter, feature, and entitlement are created for the test subject.

    Returns:
        A configured MeteringService instance
    """

    # Create a custom MeteringService that uses the local OpenMeter instance
    class LocalMeteringService(MeteringService):
        @staticmethod
        def _create_client() -> AsyncClient:
            """Create and return an OpenMeter client pointing to the local instance."""
            headers = {
                'Accept': 'application/json',
            }

            return AsyncClient(
                endpoint='http://localhost:8888',
                headers=headers,
            )

    # Return the custom service
    service = LocalMeteringService()

    # Override the OPENMETER_FEATURE_KEY setting for this test
    original_feature_key = settings.OPENMETER_FEATURE_KEY
    settings.OPENMETER_FEATURE_KEY = local_feature

    yield service

    # Restore the original feature key
    settings.OPENMETER_FEATURE_KEY = original_feature_key
