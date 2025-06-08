from fastapi.testclient import TestClient

from src.keywords.models import KeywordRequest
from src.main import app

client = TestClient(app)


def test_extract_keywords_valid_input():
    request_data = KeywordRequest(text='Extract keywords from this text.').model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['keywords', 'Extract', 'text', 'Extract keywords']
    assert (
        response_data['highlighted_text']
        == '<kw>Extract</kw> <kw>keywords</kw> from this <kw>text</kw>.'
    )


def test_extract_keywords_valid_input_with_language():
    request_data = KeywordRequest(
        text='Extrahiere Worte von diesem Text', language='de'
    ).model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['Extrahiere', 'Worte', 'Text', 'Extrahiere Worte']


def test_extract_keywords_valid_input_with_max_ngram_size():
    request_data = KeywordRequest(
        text='Extract keywords from this text.', max_ngram_size=1
    ).model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['keywords', 'Extract', 'text']


def test_extract_keywords_valid_input_with_min_score():
    request_data = KeywordRequest(
        text='Extract keywords from this text.', min_score=0.2
    ).model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['keywords']


def test_extract_keywords_valid_input_with_max_keywords():
    request_data = KeywordRequest(
        text='Extract keywords from this text.', max_keywords=2
    ).model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['Extract', 'Extract keywords']


def test_extract_keywords_valid_input_with_deduplication_threshold():
    request_data = KeywordRequest(
        text='Extract keywords from this text.', deduplication_threshold=0.5
    ).model_dump()
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['keywords'] == ['keywords', 'Extract', 'text', 'Extract keywords']


def test_extract_keywords_missing_text():
    request_data = {}
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 422


def test_extract_keywords_empty_text():
    request_data = {'text': ''}
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 200


def test_extract_keywords_invalid_text_type():
    request_data = {'text': 12345}
    response = client.post('/api/keywords/extract/', json=request_data)
    assert response.status_code == 422
