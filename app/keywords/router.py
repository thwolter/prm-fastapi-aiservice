import logging

from fastapi import APIRouter, HTTPException

from app.keywords.keywords import get_keywords
from app.keywords.models import KeywordRequest, KeywordResponse

router = APIRouter(
    prefix='/api',
    tags=['api'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/keywords/extract/', response_model=KeywordResponse)
def extract_keywords(request: KeywordRequest) -> KeywordResponse:
    try:
        result = get_keywords(request)
        return result
    except Exception as e:
        logging.error(f'Error extracting keywords: {e}')
        raise HTTPException(status_code=500, detail='Error extracting keywords')
