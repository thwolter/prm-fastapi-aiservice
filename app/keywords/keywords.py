import yake
from yake.highlight import TextHighlighter

from app.keywords.models import KeywordRequest, KeywordResponse

kw_extractor = yake.KeywordExtractor()
th = TextHighlighter(max_ngram_size=3)


def get_keywords(request: KeywordRequest) -> KeywordResponse:
    kw_extractor = yake.KeywordExtractor(
        lan=request.language,
        n=request.max_ngram_size,
        dedupLim=request.deduplication_threshold,
        dedupFunc=request.deduplication_algo,
        windowsSize=request.window_size,
        top=request.max_keywords,
        features=request.features,
        stopwords=request.stopwords,
    )

    extracted_keywords = sorted(
        kw_extractor.extract_keywords(request.text), key=lambda x: x[1], reverse=True
    )
    keywords = [(kw, score) for kw, score in extracted_keywords if score >= request.min_score]

    highlighted_text = th.highlight(request.text, keywords)
    return KeywordResponse(keywords=[kw for kw, _ in keywords], highlighted_text=highlighted_text)
