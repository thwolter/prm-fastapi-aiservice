from fastapi.testclient import TestClient

from app.keywords.models import KeywordRequest
from app.main import app

client = TestClient(app)


def test_extract_keywords_valid_input():
    request_data = KeywordRequest(text="Extract keywords from this text.").model_dump()
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["keywords"] == ['Extract keywords', 'Extract', 'text', 'keywords']
    assert response_data["highlighted_text"] == '<kw>Extract keywords</kw> from this <kw>text</kw>.'


def test_extract_keywords_valid_input_with_language():
    request_data = KeywordRequest(text="Extrair palavras-chave deste texto.", language="pt").model_dump()
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["keywords"] == [
        'Extrair palavras-chave deste', 'palavras-chave deste texto',
        'Extrair palavras-chave', 'deste texto', 'palavras-chave deste', 'Extrair',
        'texto', 'palavras-chave', 'deste'
    ]


def test_extract_keywords_valid_input_with_max_ngram_size():
    request_data = KeywordRequest(text="Extract keywords from this text.", max_ngram_size=2).model_dump()
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["keywords"] == ['Extract keywords', 'Extract', 'text', 'keywords']


def test_extract_keywords_missing_text():
    request_data = {}
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 422


def test_extract_keywords_empty_text():
    request_data = {"text": ""}
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 200


def test_extract_keywords_invalid_text_type():
    request_data = {"text": 12345}
    response = client.post("/api/keywords/extract/", json=request_data)
    assert response.status_code == 422
