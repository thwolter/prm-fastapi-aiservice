from datetime import datetime, timedelta

import jwt
import pytest

from src.core.config import settings
from src.domain.models import Entitlement
from src.main import app


@pytest.fixture(autouse=True)
def override_auth(monkeypatch, request):
    """Override authentication dependencies for tests."""

    if request.node.get_closest_marker("integration"):
        yield
    else:

        async def _get_entitlement_value(self, feature_key):
            return Entitlement(
                feature_key=feature_key,
                has_access=True,
                balance=100,
                usage=0,
            )

        monkeypatch.setattr(
            "src.domain.services.entitlement_service.EntitlementService.get_entitlement_value",
            _get_entitlement_value,
        )

        yield
        app.dependency_overrides.clear()


@pytest.fixture
def auth_token():
    """Generate a valid JWT token for testing."""
    # Create token payload
    expiry = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "email": "test@example.com",
        "exp": expiry,
        "aud": settings.AUTH_TOKEN_AUDIENCE,
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
    return {"Authorization": f"Bearer {auth_token}"}
