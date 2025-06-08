import logging
import sys

from .config import settings


LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname == 'INFO':
            levelname = 'INFO:    '
        elif levelname == 'DEBUG':
            levelname = 'DEBUG:   '
        elif levelname == 'WARNING':
            levelname = 'WARNING: '
        elif levelname == 'ERROR':
            levelname = 'ERROR:   '
        elif levelname == 'CRITICAL':
            levelname = 'CRITICAL:'
        record.levelname = levelname
        return super().format(record)


formatter = CustomFormatter('%(levelname)s [%(name)s] %(message)s')


def configure_logging(level: int = LOG_LEVEL, stream=sys.stdout) -> None:
    """Configure root logging with the custom formatter."""
    logging.basicConfig(level=level, handlers=[logging.StreamHandler(stream)], force=True)
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)


configure_logging()
