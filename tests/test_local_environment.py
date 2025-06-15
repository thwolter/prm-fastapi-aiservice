from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from src.auth.dependencies import get_current_user
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
from src.core.config import settings
from src.middleware.authorization_middleware import AuthorizationMiddleware

# Test app with user authentication dependency
app_user_auth = FastAPI()


@app_user_auth.get("/user-protected")
async def user_protected(user=Depends(get_current_user)):
    return {"user": user}


# Test app with token service
app_token_service = FastAPI()
app_token_service.add_middleware(AuthorizationMiddleware)


@app_token_service.get("/token-check")
async def token_check(request: Request):
    entitlement_service = TokenQuotaServiceProvider.get_entitlement_service(request)
    has_access = await entitlement_service.get_token_entitlement_status(
        None, settings.OPENMETER_FEATURE_KEY
    )
    return {"has_access": has_access}


@app_token_service.get("/token-consume")
async def token_consume(request: Request):
    token_service = TokenQuotaServiceProvider.get_token_consumption_service(request)

    # Create a dummy result object with tokens_info
    class DummyResult:
        def __init__(self):
            self.tokens_info = {
                "total_tokens": 100,
                "model_name": "test-model",
                "prompt_name": "test-prompt",
            }

    result = DummyResult()
    # First reserve tokens
    await token_service.reserve_token_quota(50)
    # Then adjust consumed tokens
    await token_service.adjust_consumed_tokens(result, UUID("00000000-0000-0000-0000-000000000000"))
    return {"consumed": True}


def test_user_auth_local_environment(monkeypatch):
    """Test that user authentication is bypassed in the local environment."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "local")
    with TestClient(app_user_auth) as client:
        # No token provided, but should still work in local environment
        res = client.get("/user-protected")
        assert res.status_code == 200
        assert "user" in res.json()


def test_token_service_entitlement_status_local_environment(monkeypatch):
    """Test that token entitlement checking is bypassed in the local environment."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "local")
    with TestClient(app_token_service) as client:
        # No token provided, but should still have access in local environment
        res = client.get("/token-check")
        assert res.status_code == 200
        assert res.json() == {"has_access": True}
