import uuid

import pytest


@pytest.mark.asyncio
async def test_token_consumption_with_local_openmeter(local_metering_service, test_subject_id):
    """
    Test that demonstrates how to use the local OpenMeter fixtures.

    This test checks that:
    1. The subject has an initial balance of 1000 tokens
    2. After consuming 50 tokens, the balance is reduced to 950 tokens
    """
    # Check initial entitlement
    entitlement = await local_metering_service.check_entitlement(uuid.UUID(test_subject_id))
    assert entitlement['has_access'] is True
    assert entitlement['balance'] == 1000

    # Consume tokens
    result = await local_metering_service.consume_tokens(
        uuid.UUID(test_subject_id), tokens=50, model='test-model', prompt='test-prompt'
    )
    assert result is True

    # Check updated balance
    updated_entitlement = await local_metering_service.check_entitlement(uuid.UUID(test_subject_id))
    assert updated_entitlement['has_access'] is True
    assert updated_entitlement['balance'] == 950


@pytest.mark.integration
@pytest.mark.asyncio
async def test_insufficient_tokens_with_local_openmeter(local_metering_service, test_subject_id):
    """
    Test that demonstrates handling insufficient token balance.

    This test checks that:
    1. After consuming all available tokens, the balance is 0
    2. The subject no longer has access
    """
    # Consume all tokens (1000)
    result = await local_metering_service.consume_tokens(
        uuid.UUID(test_subject_id), tokens=1000, model='test-model', prompt='test-prompt'
    )
    assert result is True

    # Check updated balance
    updated_entitlement = await local_metering_service.check_entitlement(uuid.UUID(test_subject_id))
    assert updated_entitlement['has_access'] is False
    assert updated_entitlement['balance'] == 0

    # Try to consume more tokens
    result = await local_metering_service.consume_tokens(
        uuid.UUID(test_subject_id), tokens=50, model='test-model', prompt='test-prompt'
    )
    # The consumption should still succeed at the API level
    # but the application should check entitlement before allowing operations
    assert result is True
