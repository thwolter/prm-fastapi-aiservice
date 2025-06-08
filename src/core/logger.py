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

logging.basicConfig(level=LOG_LEVEL, handlers=[logging.StreamHandler(sys.stdout)])


for handler in logging.root.handlers:
    handler.setFormatter(formatter)
