import logging


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
