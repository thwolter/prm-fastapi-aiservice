import pytest

from src.main import app


@pytest.fixture(autouse=True)
def override_auth(monkeypatch):
    """Override authentication dependencies for tests."""

    from fastapi import Request

    async def dummy_get_current_user(request: Request):
        return {"token": "test", "user_id": "00000000-0000-0000-0000-000000000000"}

    from src.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = dummy_get_current_user

    async def _allow(self):
        return True

    monkeypatch.setattr("src.auth.quota_service.TokenQuotaService.has_access", _allow)

    async def _consume(self, result, user_id):
        return None

    monkeypatch.setattr("src.auth.quota_service.TokenQuotaService.consume_tokens", _consume)
    yield
    app.dependency_overrides.clear()
