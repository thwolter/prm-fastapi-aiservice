"""Integration test of the OpenMeter sandbox."""

import uuid

import pytest
from fastapi import Request
from openmeter import Client

from src.auth.quota_service import TokenQuotaService
from src.core.config import settings

"""
Prerequisites
-------------
- Valid sandbox API key and URL in the environment (`OPENMETER_API_KEY` and
  `OPENMETER_API_URL`).
- Active internet connection to reach the sandbox service.

The `create_entitlement` call issues an initial allowance of ``1000`` tokens for
the temporary test subject. Both the entitlement and the subject are deleted in
the fixture teardowns so the sandbox remains clean after the test run.
"""


# Fixtures for sandbox client and test subject
@pytest.fixture(scope="module")
def sandbox_client():
    return Client(
        endpoint=settings.OPENMETER_API_URL,
        headers={"Authorization": f"Bearer {settings.OPENMETER_API_KEY}"},
    )


@pytest.fixture(scope="module")
async def test_subject(sandbox_client):
    subj_id = f"pytest-{uuid.uuid4()}"
    await sandbox_client.create(subj_id)
    yield subj_id
    # Teardown: delete subject (cascades entitlements)
    await sandbox_client.delete(subj_id)


@pytest.fixture(scope="module")
async def entitlement_setup(sandbox_client, test_subject):
    ent = await sandbox_client.create_entitlement(
        test_subject,
        featureKey="ai_tokens",
        type="metered",
        usagePeriod={"interval": "MONTH"},
        issueAfterReset=1000,  # initial grant of 1000 tokens for the test user
        isSoftLimit=False,
    )
    yield ent
    # Cleanup entitlement after test
    await sandbox_client.delete_entitlement(test_subject, ent.id)


@pytest.mark.asyncio
async def test_reserve_and_adjust_tokens(
    entitlement_setup, sandbox_client, test_subject, monkeypatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "testing123")
    req: Request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "body": {
                "model_name": "gpt-test",
                "prompt_name": "unit-test",
                "tokens": 200,
            },
            "state": {
                "token": "test_token",
                "user_id": str(test_subject),
            },
            "headers": [
                (b"authorization", f"Bearer {settings.OPENMETER_API_KEY}".encode()),
                (b"accept", b"application/json"),
            ],
        }
    )
    # Ensure we are in test environment
    service = TokenQuotaService(request=req)

    # Reserve 200 tokens
    assert await service.reserve_token_quota(200) is True

    # Simulate actual usage of 150 tokens
    result = type(
        "Res",
        (),
        {
            "tokens_info": {
                "total_tokens": 150,
                "model_name": "gpt-test",
                "prompt_name": "unit-test",
            },
            "response_info": {"time_ms": 123},
        },
    )()
    await service.adjust_consumed_tokens(result, test_subject)

    # Query remaining balance
    val = await sandbox_client.get_entitlement_value(test_subject, "ai_tokens")
    assert val["balance"] == 1000 - 200 + (200 - 150)

    # Reserve more than remaining -> should fail
    assert await service.reserve_token_quota(10000) is False
