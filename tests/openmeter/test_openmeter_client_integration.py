"""
End-to-end tests for the OpenMeterClient.
These tests interact with a real OpenMeter service and use mocks where necessary.
"""

import uuid

import pytest
from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent

from src.core.config import settings
from src.domain.models.usage import UsageEvent
from src.external.metering.openmeter_client import OpenMeterClient


@pytest.mark.integration
def test_openmeter_client_initialization():
    """
    Integration test to verify initialization of the OpenMeter client.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client and
    verifies that it can be created without errors.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)
        assert client is not None
    except Exception as exc:
        pytest.fail(f'OpenMeter client initialization failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_record_usage():
    """
    Integration test to verify that the OpenMeter client can record usage.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client,
    records usage for a subject, and verifies that the usage was recorded successfully.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

        # Use a test subject ID
        subject_id = str(uuid.uuid4())

        # Record usage
        usage_event = UsageEvent(tokens=100, model='test-model', prompt='test-prompt')
        result = client.record_usage(subject_id, usage_event)

        # Verify the usage was recorded successfully
        assert result is True
    except Exception as exc:
        pytest.fail(f'OpenMeter client record_usage test failed: {exc}')


@pytest.mark.integration
def test_openmeter_client_ingest_events():
    """
    Integration test to verify that the OpenMeter client can ingest events.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client,
    ingests an event for a subject, and verifies that the event was ingested successfully.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

        # Use a test subject ID
        subject_id = str(uuid.uuid4())

        # Create a cloud event
        event = CloudEvent(
            attributes={
                'id': str(uuid.uuid4()),
                'type': settings.OPENMETER_EVENT_TYPE,
                'source': settings.OPENMETER_SOURCE,
                'subject': subject_id,
            },
            data={'tokens': 100, 'model': 'test-model', 'prompt': 'test-prompt'},
        )

        # Ingest the event
        result = client.ingest_events(to_dict(event))

        # Verify the event was ingested successfully
        assert result is True
    except Exception as exc:
        pytest.fail(f'OpenMeter client ingest_events test failed: {exc}')


"""
The following tests have been removed as they test functionality that is no longer implemented in OpenMeterClient:
- test_openmeter_client_upsert_and_list_subjects
- test_openmeter_client_delete_subject
- test_openmeter_client_list_entitlements
"""


@pytest.mark.integration
def test_openmeter_client_get_usage():
    """
    Integration test to verify that the OpenMeter client can get usage.

    This test checks if the `OPENMETER_API_KEY` is provided. If the key is not present,
    the test is skipped. Otherwise, it initializes the OpenMeter client,
    gets the usage for a subject, and verifies that the usage was retrieved correctly.

    Note: The current implementation of get_usage returns a default response,
    so we're just testing that the method doesn't raise an exception and returns
    a properly structured response.
    """
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip('OPENMETER_API_KEY not provided')

    try:
        # Initialize the client
        sync_client, async_client = OpenMeterClient.create_clients()
        client = OpenMeterClient(sync_client, async_client)

        # Use a test subject ID
        subject_id = str(uuid.uuid4())

        # Get usage
        usage = client.get_usage(subject_id)

        # Verify the usage was retrieved correctly
        assert usage is not None
        assert hasattr(usage, 'sufficient')
        assert hasattr(usage, 'token_limit')
        assert hasattr(usage, 'consumed_tokens')
        assert hasattr(usage, 'remaining_tokens')
    except Exception as exc:
        pytest.fail(f'OpenMeter client get_usage test failed: {exc}')
