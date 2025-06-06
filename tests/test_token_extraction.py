import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.middleware.token_extraction import TokenExtractionMiddleware


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(TokenExtractionMiddleware)

    @app.get('/dummy')
    async def dummy(request: Request):
        return {
            'token': getattr(request.state, 'token', None),
            'user_id': getattr(request.state, 'user_id', None),
        }

    return app


def test_valid_cookie_sets_state():
    app = create_app()
    token = 'validtoken'
    with patch('app.middleware.token_extraction.get_jwt_payload') as mock_payload:
        mock_payload.return_value = {'sub': 'user123'}
        with TestClient(app) as client:
            response = client.get('/dummy', cookies={'auth': token})
            assert response.status_code == 200
            assert response.json() == {'token': token, 'user_id': 'user123'}
        mock_payload.assert_called_once()


def test_no_cookie_results_in_none():
    app = create_app()
    with patch('app.middleware.token_extraction.get_jwt_payload') as mock_payload:
        with TestClient(app) as client:
            response = client.get('/dummy')
            assert response.status_code == 200
            assert response.json() == {'token': None, 'user_id': None}
        mock_payload.assert_not_called()
