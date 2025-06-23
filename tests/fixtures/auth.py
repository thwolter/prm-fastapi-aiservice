"""
Authentication fixtures for testing.

This file contains fixtures for authentication and authorization in tests.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pytest

from src.core.config import settings


@pytest.fixture(autouse=True)
def override_auth(monkeypatch, request):
    """
    Override authentication dependencies for tests.

    This fixture mocks the metering service for non-integration tests to bypass
    token consumption and entitlement checks. For integration tests, it does nothing,
    allowing the actual metering service to be used.

    Args:
        monkeypatch: Pytest's monkeypatch fixture for modifying behavior.
        request: Pytest's request fixture for accessing test metadata.

    Yields:
        None
    """
    if request.node.get_closest_marker('openmeter'):
        # For integration tests, don't mock anything
        yield
    else:
        # For non-integration tests, mock the metering service
        monkeypatch.setattr(
            'src.services.metering_service.MeteringService.check_entitlement',
            AsyncMock(return_value={'hasAccess': True, 'balance': 100}),
        )
        monkeypatch.setattr(
            'src.services.metering_service.MeteringService.consume_tokens',
            AsyncMock(return_value=True),
        )
        yield


@pytest.fixture
def auth_token():
    """
    Generate a valid JWT token for testing.

    This fixture creates a JWT token with a fixed user ID and email,
    which can be used for authentication in tests.

    Returns:
        str: A valid JWT token.
    """
    # Create token payload
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        'sub': '00000000-0000-0000-0000-000000000000',
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
    return token


@pytest.fixture
def auth_headers(auth_token):
    """
    Return headers with a valid JWT token.

    This fixture creates HTTP headers with an Authorization header
    containing a valid JWT token, which can be used for authenticated
    requests in tests.

    Args:
        auth_token: A valid JWT token from the auth_token fixture.

    Returns:
        dict: HTTP headers with an Authorization header.
    """
    return {'Authorization': f'Bearer {auth_token}'}
