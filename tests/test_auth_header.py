from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.auth.dependencies import get_current_user
from src.core.config import settings
from src.middleware.user_token_extraction import UserTokenExtractionMiddleware

app = FastAPI()
app.add_middleware(UserTokenExtractionMiddleware)


@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"user": user}


def test_missing_authorization_header(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with TestClient(app) as client:
        res = client.get("/protected")
        assert res.status_code == 401


def test_invalid_authorization_header(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with TestClient(app) as client:
        res = client.get("/protected", headers={"Authorization": "Token invalid"})
        assert res.status_code == 401
