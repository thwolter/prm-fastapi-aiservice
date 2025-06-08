from typing import Optional

from pydantic import BaseModel, Field


class KeywordRequest(BaseModel):
    text: str = Field(..., description='The text to be used for keyword extraction.')
    language: Optional[str] = 'en'
    max_ngram_size: Optional[int] = 3
    deduplication_threshold: Optional[float] = 0.9
    deduplication_algo: Optional[str] = 'seqm'
    window_size: Optional[int] = 1
    max_keywords: Optional[int] = 20
    min_score: Optional[float] = 0.0
    features: Optional[list[str]] = None
    stopwords: Optional[list[str]] = None


class KeywordResponse(BaseModel):
    keywords: list[str] = Field(..., description='The list of keywords extracted.')
    highlighted_text: str = Field(..., description='The text with keywords highlighted.')
