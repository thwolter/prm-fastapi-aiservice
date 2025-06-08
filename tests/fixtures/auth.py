import pytest

from src.main import app


@pytest.fixture(autouse=True)
def override_auth(monkeypatch):
    """Override authentication dependencies for tests."""

    async def dummy_get_current_user(request):
        return {'token': 'test', 'user_id': '00000000-0000-0000-0000-000000000000'}

    from src.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = dummy_get_current_user
    monkeypatch.setattr('src.auth.service.TokenService.has_access', lambda self: True)
    monkeypatch.setattr(
        'src.auth.service.TokenService.consume_tokens',
        lambda self, result, user_id: None,
    )
    yield
    app.dependency_overrides.clear()
