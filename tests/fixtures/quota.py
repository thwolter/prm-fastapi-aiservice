import uuid

import pytest
from fastapi import Request

from src.auth.quota_service import TokenQuotaService
from src.auth.schemas import EntitlementCreate


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def test_subject(mock_openmeter_clients):
    """
    Create a test subject with an entitlement of 1000 tokens per month.
    Uses the mock OpenMeter client instead of the actual one.
    """
    sync_client, async_client = mock_openmeter_clients
    subject_id = str(uuid.uuid4())
    req: Request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": subject_id,
                "user_email": "test@example.com",
            },
        }
    )
    service = TokenQuotaService(request=req)
    await service.create_customer()

    # Verify customer was created
    assert subject_id in sync_client.subjects, "Subject should be created in OpenMeter"

    # Add entitlement setup
    limit = EntitlementCreate(feature="ai_tokens", max_limit=1000, period="MONTH")
    await service.set_entitlement(limit)

    # Verify entitlement was set
    assert subject_id in sync_client.entitlements, "Subject should have entitlements"
    assert (
        "ai_tokens" in sync_client.entitlements[subject_id]
    ), "Subject should have ai_tokens entitlement"
    assert (
        sync_client.entitlements[subject_id]["ai_tokens"]["balance"] == 1000
    ), "Initial balance should be 1000"

    yield subject_id  # Return the subject_id for use in tests

    # Clean up by deleting the customer
    await service.delete_customer()

    # Verify cleanup
    assert subject_id not in sync_client.subjects, "Subject should be deleted from OpenMeter"
