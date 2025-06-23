"""
OpenMeter fixtures for integration testing.

This file contains fixtures for setting up and interacting with a local OpenMeter instance
for integration testing. These fixtures are only used when tests are marked with the
'integration' marker.
"""

import uuid
from datetime import datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from azure.core.exceptions import ResourceExistsError
from openmeter import Client
from openmeter.aio import Client as AsyncClient

from src.core.config import settings
from src.services.metering_service import MeteringService


@pytest_asyncio.fixture(scope='session')
def local_openmeter_clients():
    """
    Provide OpenMeter clients configured to use the local instance.

    This fixture connects to the local OpenMeter instance specified by
    ``settings.OPENMETER_API_URL`` (e.g., ``http://localhost:8888``) as described
    in the README.md. No authentication is required for the local instance.

    The fixture is session-scoped to avoid creating new clients for each test,
    which improves test performance.

    Returns:
        tuple: A tuple containing (sync_client, async_client)
    """
    # Local OpenMeter instance URL
    local_endpoint = settings.OPENMETER_API_URL

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
    Provide a unique subject ID for testing.

    This fixture generates a random UUID to use as a subject ID in tests,
    ensuring that each test has a unique subject ID to avoid conflicts.

    Returns:
        str: A unique subject ID as a string.
    """
    return str(uuid.uuid4())


@pytest_asyncio.fixture
async def local_meter(local_openmeter_clients):
    """
    Create a meter in the local OpenMeter instance for testing.

    This fixture creates a meter with a unique ID in the local OpenMeter instance,
    and automatically cleans it up after the test is complete. The meter is configured
    to count tokens as defined in the application settings.

    Args:
        local_openmeter_clients: The OpenMeter clients from the local_openmeter_clients fixture.

    Yields:
        str: The ID of the created meter.
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
    Create a feature in the local OpenMeter instance for testing.

    This fixture creates a feature with a unique ID in the local OpenMeter instance,
    linked to the meter created by the local_meter fixture. The feature is configured
    with a monthly reset period, and is automatically cleaned up after the test is complete.

    Args:
        local_openmeter_clients: The OpenMeter clients from the local_openmeter_clients fixture.
        local_meter: The meter ID from the local_meter fixture.

    Yields:
        str: The ID of the created feature.
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
    Create an entitlement in the local OpenMeter instance for testing.

    This fixture creates an entitlement for the test subject with the specified feature,
    giving the subject an initial token balance of 1000. The entitlement is automatically
    cleaned up after the test is complete.

    Args:
        local_openmeter_clients: The OpenMeter clients from the local_openmeter_clients fixture.
        local_feature: The feature ID from the local_feature fixture.
        test_subject_id: The subject ID from the test_subject_id fixture.

    Yields:
        dict: The created entitlement object with subject_id, feature_id, and limit.
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
async def local_metering_client():
    """
    Fixture to create an OpenMeter client for testing purposes.

    This fixture creates an async OpenMeter client that connects to the local
    OpenMeter instance specified by settings.OPENMETER_LOCAL_API_URL.
    """
    client = AsyncClient(endpoint=settings.OPENMETER_LOCAL_API_URL)
    yield client
    await client.close()


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_meter_for_tokens(local_metering_client):
    """
    Fixture to create a meter for token testing purposes.

    This fixture creates a meter specifically for testing token consumption
    with the risk definition check service.
    """
    meter_payload = {
        'name': 'ai_tokens',
        'slug': 'ai_tokens',
        'description': 'LLM tokens',
        'eventType': 'tokens',
        'valueProperty': '$.tokens',
        'aggregation': 'SUM',
        'groupBy': {
            'model': '$.model',
            'prompt': '$.prompt',
        },
        'metadata': None,
    }
    try:
        created_meter = await local_metering_client.create_meter(meter_payload)
        assert created_meter is not None, 'Meter creation failed'
    except ResourceExistsError:
        created_meter = await local_metering_client.get_meter(meter_payload['slug'])

    yield created_meter

    try:
        await local_metering_client.delete_meter(meter_payload['slug'])
    except ResourceExistsError:
        # If an active feature is present, we cannot delete the entitlement
        pass


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_feature_for_tokens(local_metering_client, local_meter_for_tokens):
    """
    Fixture to create a feature for token testing purposes.

    This fixture creates a feature specifically for testing token consumption
    with the risk definition check service.
    """
    feature_payload = {
        'key': settings.OPENMETER_FEATURE_KEY,
        'meterSlug': 'ai_tokens',
        'name': 'Ai Tokens',
    }

    try:
        created_feature = await local_metering_client.create_feature(feature_payload)
        assert created_feature is not None, 'Feature creation failed'
    except ResourceExistsError:
        created_feature = await local_metering_client.get_feature(feature_payload['key'])
    yield created_feature
    local_metering_client.delete_feature(feature_payload['key'])


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_subject_for_tokens(local_metering_client):
    """
    Fixture to create a subject for token testing purposes.

    This fixture creates a subject specifically for testing token consumption
    with the risk definition check service.
    """
    subject_payload = {
        'key': 'user_001',
        'displayname': 'Test User',
    }

    created_subject = await local_metering_client.upsert_subject([subject_payload])
    assert created_subject is not None, 'Subject creation failed'
    yield created_subject[0]
    local_metering_client.delete_subject(created_subject[0]['id'])


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_entitlement_for_tokens(
    local_metering_client,
    local_subject_for_tokens,
    local_feature_for_tokens,
    issue_after_reset=10000,
):
    """
    Fixture to create an entitlement for token testing purposes.

    This fixture creates an entitlement specifically for testing token consumption
    with the risk definition check service. The issue_after_reset parameter controls
    the initial token balance.
    """
    entitlement_payload = {
        'subjectKey': 'user_001',
        'featureKey': settings.OPENMETER_FEATURE_KEY,
        'issueAfterReset': issue_after_reset,
        'type': 'metered',
        'usagePeriod': {'interval': 'MONTH', 'startDay': 1},
    }

    created_entitlement = await local_metering_client.create_entitlement(
        local_subject_for_tokens['key'], entitlement_payload
    )
    if created_entitlement.get('title') == 'Conflict':
        entitlement_id = created_entitlement['extensions']['conflictingEntityId']
        created_entitlement = await local_metering_client.get_entitlement(
            local_subject_for_tokens['key'], entitlement_id
        )
    assert created_entitlement is not None, 'Entitlement creation failed'

    yield created_entitlement

    try:
        await local_metering_client.delete_entitlement(
            local_subject_for_tokens['id'], created_entitlement['id']
        )
    except ResourceExistsError:
        # If an active feature is present, we cannot delete the entitlement
        pass


@pytest_asyncio.fixture
@pytest.mark.integration
async def local_auth_headers(local_subject_for_tokens):
    """
    Fixture to create authentication headers for the test user.

    This fixture creates authentication headers with a JWT token for the test user,
    which can be used to make authenticated requests to the application.
    """
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        'sub': local_subject_for_tokens['key'],
        'email': 'test@example.com',
        'exp': expiry,
        'aud': settings.AUTH_TOKEN_AUDIENCE,
    }
    # Encode the token
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.AUTH_TOKEN_ALGORITHM,
    )

    auth_headers = {'Authorization': f'Bearer {token}'}

    return auth_headers


@pytest_asyncio.fixture
async def local_metering_service(
    local_openmeter_clients, local_feature, local_entitlement, test_subject_id
):
    """
    Provide a MeteringService instance configured to use the local OpenMeter instance.

    This fixture creates a custom MeteringService subclass that connects to the local
    OpenMeter instance instead of the production instance. It also temporarily overrides
    the OPENMETER_FEATURE_KEY setting to use the feature created by the local_feature fixture.

    The fixture ensures that a meter, feature, and entitlement are created for the test subject
    before the MeteringService is used, and restores the original settings afterward.

    Args:
        local_openmeter_clients: The OpenMeter clients from the local_openmeter_clients fixture.
        local_feature: The feature ID from the local_feature fixture.
        local_entitlement: The entitlement from the local_entitlement fixture.
        test_subject_id: The subject ID from the test_subject_id fixture.

    Yields:
        MeteringService: A configured MeteringService instance that uses the local OpenMeter.
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
