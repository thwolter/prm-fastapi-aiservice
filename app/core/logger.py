import logging
import sys

from .config import settings
from .logging_formatter import CustomFormatter


def configure_logging(level: str | None = None, stream=sys.stdout) -> None:
    """Configure application logging."""
    level_name = level or settings.LOG_LEVEL
    log_level = getattr(logging, level_name.upper(), logging.INFO)

    handler = logging.StreamHandler(stream)
    formatter = CustomFormatter('%(levelname)s [%(name)s] %(message)s')
    handler.setFormatter(formatter)

    logging.basicConfig(level=log_level, handlers=[handler])

    for h in logging.root.handlers:
        h.setFormatter(formatter)
