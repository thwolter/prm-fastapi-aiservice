import pytest

from src.main import app


@pytest.fixture(autouse=True)
def override_auth(monkeypatch, request):
    """Override authentication dependencies for tests."""

    from fastapi import Request

    async def dummy_get_current_user(request: Request):
        return {"token": "test", "user_id": "00000000-0000-0000-0000-000000000000"}

    from src.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = dummy_get_current_user

    if request.node.get_closest_marker("no_quota_patch") is not None:

        async def _allow(self):
            return True

        async def _reserve(self, tokens):
            return True

        async def _adjust(self, result, user_id):
            return None

        monkeypatch.setattr(
            "src.auth.quota_service.TokenQuotaService.get_token_entitlement_status", _allow
        )

        monkeypatch.setattr(
            "src.auth.quota_service.TokenQuotaService.reserve_token_quota", _reserve
        )

        monkeypatch.setattr(
            "src.auth.quota_service.TokenQuotaService.adjust_consumed_tokens", _adjust
        )

    yield
    app.dependency_overrides.clear()
