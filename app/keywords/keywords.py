import yake
from yake.highlight import TextHighlighter

from app.keywords.models import KeywordRequest, KeywordResponse

kw_extractor = yake.KeywordExtractor()
th = TextHighlighter(max_ngram_size = 3)


def get_keywords(request: KeywordRequest) -> KeywordResponse:
    kw_extractor.language = request.language
    kw_extractor.max_ngram_size = request.max_ngram_size
    kw_extractor.deduplication_threshold = request.deduplication_threshold
    kw_extractor.deduplication_algo = request.deduplication_algo
    kw_extractor.windowSize = request.window_size
    kw_extractor.numOfKeywords = request.max_Keywords
    kw_extractor.min_score = request.min_score

    extracted_keywords = kw_extractor.extract_keywords(request.text)
    keywords = [(kw, score) for kw, score in extracted_keywords]
    highlighted_text = th.highlight(request.text, keywords)
    return KeywordResponse(
        keywords=[kw for kw, _ in keywords],
        highlighted_text=highlighted_text
    )
