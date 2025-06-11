import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.auth.dependencies import verify_service_jwt
from src.core.config import settings

app = FastAPI(dependencies=[Depends(verify_service_jwt)])


@app.get("/protected")
async def protected():
    return {"ok": True}


def _make_token(**payload):
    data = {"iss": "projectrm-backend", "exp": datetime.utcnow() + timedelta(minutes=5)}
    data.update(payload)
    return jwt.encode(data, settings.SERVICE_SECRET, algorithm=settings.AUTH_TOKEN_ALGORITHM)


def test_service_jwt_valid(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    token = _make_token()
    with TestClient(app) as client:
        res = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json() == {"ok": True}


def test_service_jwt_invalid(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    token = _make_token(iss="other")
    with TestClient(app) as client:
        res = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401
