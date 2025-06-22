from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pytest

from src.core.config import settings


@pytest.fixture(autouse=True)
def override_auth(monkeypatch, request):
    """Override authentication dependencies for tests."""

    if request.node.get_closest_marker('integration'):
        yield
    else:
        monkeypatch.setattr(
            'src.services.metering_service.MeteringService.check_entitlement',
            AsyncMock(return_value={'has_access': True, 'balance': 100}),
        )
        monkeypatch.setattr(
            'src.services.metering_service.MeteringService.consume_tokens',
            AsyncMock(return_value=True),
        )
        yield


@pytest.fixture
def auth_token():
    """Generate a valid JWT token for testing."""
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
    """Return headers with a valid JWT token."""
    return {'Authorization': f'Bearer {auth_token}'}
