"""Tests for the logutils module."""
from src.utils import logutils as logger_logging, logutils as original_logging
from unittest import mock

from src.utils.logutils.formatters import CustomFormatter


def test_logger_exports():
    """Test that the logutils module exports the expected symbols."""
    # Check that the module exports the standard logutils module
    # The logger_logging is not the same as the standard logutils module,
    # but it should provide the same functionality
    assert hasattr(logger_logging, 'get_logger')
    assert callable(logger_logging.get_logger)

    # Check that the CustomFormatter class is available from the src.utils.logutils module
    from src.utils.logutils import CustomFormatter as exported_formatter
    assert exported_formatter == CustomFormatter
