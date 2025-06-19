"""
Dependencies for FastAPI.
"""

from fastapi import Request
from riskgpt.models.schemas import BaseResponse

from src.core.config import settings
from src.domain.services import (
    EntitlementService,
    MeteringService,
    PaymentService,
    SubjectService,
    SubscriptionService,
)
from src.external.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient
from src.external.metering.openmeter_client import OpenMeterClient
from src.external.payment.openmeter_payment_client import OpenMeterPaymentClient


def get_metering_client():
    """
    Get the appropriate metering client based on configuration.

    Returns:
        An instance of a class implementing AbstractMeteringClient.
    """
    if settings.METERING_VENDOR == "openmeter":
        sync_client, async_client = OpenMeterClient.create_clients()
        return OpenMeterClient(sync_client, async_client)
    # Add more vendors as needed
    raise ValueError(f"Unknown metering vendor: {settings.METERING_VENDOR}")


def get_entitlement_client():
    """
    Get the appropriate entitlement client based on configuration.

    Returns:
        An instance of a class implementing AbstractEntitlementClient.
    """
    if settings.ENTITLEMENT_VENDOR == "openmeter":
        sync_client, async_client = OpenMeterEntitlementClient.create_clients()
        return OpenMeterEntitlementClient(sync_client, async_client)
    # Add more vendors as needed
    raise ValueError(f"Unknown entitlement vendor: {settings.ENTITLEMENT_VENDOR}")


def get_subject_service(request: Request = None):
    """
    Get a SubjectService instance.

    Args:
        request: Optional FastAPI request object.

    Returns:
        A SubjectService instance.
    """
    metering_client = get_metering_client()
    return SubjectService(metering_client, request)


def get_entitlement_service(request: Request = None):
    """
    Get an EntitlementService instance.

    Args:
        request: Optional FastAPI request object.

    Returns:
        An EntitlementService instance.
    """
    entitlement_client = get_entitlement_client()
    return EntitlementService(entitlement_client, request)


def get_metering_service(request: BaseResponse = None):
    """
    Get a MeteringService instance.

    Args:
        request: Optional BaseResponse object.

    Returns:
        A MeteringService instance.
    """
    metering_client = get_metering_client()
    return MeteringService(metering_client, request)


def get_payment_client():
    """
    Get the appropriate payment client based on configuration.

    Returns:
        An instance of a class implementing AbstractPaymentClient.
    """
    if settings.PAYMENT_VENDOR == "openmeter":
        sync_client, async_client = OpenMeterPaymentClient.create_clients()
        return OpenMeterPaymentClient(sync_client, async_client)
    # Add more vendors as needed
    raise ValueError(f"Unknown payment vendor: {settings.PAYMENT_VENDOR}")


def get_payment_service():
    """
    Get a PaymentService instance.

    Returns:
        A PaymentService instance.
    """
    payment_client = get_payment_client()
    return PaymentService(payment_client)


def get_subscription_service():
    """
    Get a SubscriptionService instance.

    Returns:
        A SubscriptionService instance.
    """
    payment_service = get_payment_service()
    return SubscriptionService(payment_service)


# For testing purposes
_test_request = None


def setup_for_testing(test_user_id):
    """
    Set up the dependencies for testing with a test user ID.

    Args:
        test_user_id: The test user ID to use.
    """
    global _test_request
    # Create a mock request with the test user ID
    from fastapi import Request

    _test_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"accept", b"application/json")],
            "state": {
                "token": "test_token",
                "user_id": test_user_id,
            },
        }
    )
