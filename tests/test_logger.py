import io
import logging

from app.core.logger import CustomFormatter, configure_logging


def test_custom_formatter_levels():
    fmt = CustomFormatter('%(levelname)s %(message)s')
    cases = {
        logging.INFO: 'INFO:    ',
        logging.DEBUG: 'DEBUG:   ',
        logging.WARNING: 'WARNING: ',
        logging.ERROR: 'ERROR:   ',
        logging.CRITICAL: 'CRITICAL:',
    }
    for level, expected in cases.items():
        record = logging.LogRecord(
            name='test', level=level, pathname=__file__, lineno=1, msg='msg', args=(), exc_info=None
        )
        formatted = fmt.format(record)
        assert formatted.startswith(expected)


def test_configure_logging_sets_level_and_format(monkeypatch):
    stream = io.StringIO()
    configure_logging(level=logging.DEBUG, stream=stream)
    logger = logging.getLogger('sample')
    logger.debug('hello')
    output = stream.getvalue()
    assert 'DEBUG:    [sample] hello' in output
    assert logging.getLogger().level == logging.DEBUG
