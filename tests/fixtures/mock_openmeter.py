"""
Mock OpenMeter client for testing.
"""

import json
from functools import wraps
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
from azure.core.exceptions import ResourceNotFoundError

from src.auth.token_quota_service_provider import TokenQuotaServiceProvider


class MockOpenMeterClient(MagicMock):
    """
    Mock for the OpenMeter client.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subjects = {}
        self.entitlements = {}
        self.events = []

    def upsert_subject(self, subjects: List[Dict[str, Any]]) -> None:
        """
        Mock implementation of upsert_subject.
        """
        for subject in subjects:
            self.subjects[subject["key"]] = subject

    def delete_subject(self, subject_id: str) -> None:
        """
        Mock implementation of delete_subject.
        """
        if subject_id not in self.subjects:
            raise ResourceNotFoundError(message=f"Subject {subject_id} not found")
        del self.subjects[subject_id]

    def create_entitlement(self, subject_id: str, entitlement: Dict[str, Any]) -> None:
        """
        Mock implementation of create_entitlement.
        """
        if subject_id not in self.subjects:
            raise ResourceNotFoundError(message=f"Subject {subject_id} not found")

        if subject_id not in self.entitlements:
            self.entitlements[subject_id] = {}

        feature_key = entitlement["featureKey"]
        self.entitlements[subject_id][feature_key] = {
            "type": entitlement["type"],
            "featureKey": feature_key,
            "issueAfterReset": entitlement["issueAfterReset"],
            "usagePeriod": entitlement["usagePeriod"],
            "balance": entitlement["issueAfterReset"],
            "hasAccess": True,
        }

    def get_entitlement_value(self, subject_id: str, feature_key: str) -> Dict[str, Any]:
        """
        Mock implementation of get_entitlement_value.
        """
        if subject_id not in self.subjects:
            raise ResourceNotFoundError(message=f"Subject {subject_id} not found")

        if subject_id not in self.entitlements or feature_key not in self.entitlements[subject_id]:
            raise ResourceNotFoundError(
                message=f"Entitlement {feature_key} not found for subject {subject_id}"
            )

        return self.entitlements[subject_id][feature_key]

    def ingest_events(self, event: Dict[str, Any]) -> None:
        """
        Mock implementation of ingest_events.
        """
        self.events.append(event)

        # Adjust the balance based on the event
        subject_id = event["subject"]
        if subject_id in self.entitlements and "ai_tokens" in self.entitlements[subject_id]:
            self.entitlements[subject_id]["ai_tokens"]["balance"] -= event["data"]["tokens"]

            # Update hasAccess based on balance
            self.entitlements[subject_id]["ai_tokens"]["hasAccess"] = (
                self.entitlements[subject_id]["ai_tokens"]["balance"] > 0
            )

    async def send_request(self, request):
        """
        Mock implementation of send_request.
        """
        # Extract subject_id from URL
        url_parts = request.url.split("/")
        subject_id = url_parts[2]
        feature_key = url_parts[4]

        if subject_id not in self.subjects:
            raise ResourceNotFoundError(message=f"Subject {subject_id} not found")

        if subject_id not in self.entitlements or feature_key not in self.entitlements[subject_id]:
            raise ResourceNotFoundError(
                message=f"Entitlement {feature_key} not found for subject {subject_id}"
            )

        # Extract amount from request body
        body = request.content
        if isinstance(body, (bytes, bytearray)):
            body = body.decode()
        amount = json.loads(body)["amount"]

        # Check if there's enough balance
        if self.entitlements[subject_id][feature_key]["balance"] < amount:

            class SimpleResponse:
                def __init__(self, status_code):
                    self.status_code = status_code

            return SimpleResponse(403)

        # Decrement the balance
        self.entitlements[subject_id][feature_key]["balance"] -= amount

        # Update hasAccess based on balance
        self.entitlements[subject_id][feature_key]["hasAccess"] = (
            self.entitlements[subject_id][feature_key]["balance"] > 0
        )

        class SimpleResponse:
            def __init__(self, status_code):
                self.status_code = status_code

        return SimpleResponse(200)


class MockAsyncOpenMeterClient(MockOpenMeterClient):
    """
    Mock for the async OpenMeter client.
    """

    pass


@pytest.fixture
def mock_openmeter_clients(monkeypatch):
    """
    Fixture that provides mock OpenMeter clients and patches the TokenQuotaServiceProvider.
    Also patches the is_local_env property to return False during tests.
    """
    sync_client = MockOpenMeterClient()
    async_client = MockAsyncOpenMeterClient()
    async_client.subjects = sync_client.subjects
    async_client.entitlements = sync_client.entitlements
    async_client.events = sync_client.events

    # Patch the create_clients method to return our mock clients
    def mock_create_clients(*args, **kwargs):
        return sync_client, async_client

    monkeypatch.setattr(TokenQuotaServiceProvider, "create_clients", mock_create_clients)

    # Patch the is_local_env property in all services to return False
    from src.auth.entitlement_service import EntitlementService
    from src.auth.subject_service import SubjectService
    from src.auth.token_consumption_service import TokenConsumptionService

    monkeypatch.setattr(SubjectService, "is_local_env", property(lambda self: False))
    monkeypatch.setattr(EntitlementService, "is_local_env", property(lambda self: False))
    monkeypatch.setattr(TokenConsumptionService, "is_local_env", property(lambda self: False))

    # Patch the with_resilient_execution decorator to pass through ResourceNotFoundException
    from src.utils import resilient
    from src.utils.exceptions import ResourceNotFoundException

    original_with_resilient_execution = resilient.with_resilient_execution

    def patched_with_resilient_execution(service_name, create_default_response=None):
        original_decorator = original_with_resilient_execution(
            service_name, create_default_response
        )

        def new_decorator(func):
            original_wrapper = original_decorator(func)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await original_wrapper(*args, **kwargs)
                except Exception as e:
                    if "ResourceNotFound" in str(e):
                        raise ResourceNotFoundException(detail="User not found")
                    raise

            return wrapper

        return new_decorator

    monkeypatch.setattr(resilient, "with_resilient_execution", patched_with_resilient_execution)

    return sync_client, async_client
