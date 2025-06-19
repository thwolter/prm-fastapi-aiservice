from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.config import settings
from src.middleware.authorization_middleware import AuthorizationMiddleware

app = FastAPI()
app.add_middleware(AuthorizationMiddleware)


@app.get("/protected")
async def protected():
    return {"user": ""}


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
