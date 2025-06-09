"""Tests for the logutils module."""
from src.utils import logutils as logger_logging, logutils as original_logging
from unittest import mock

from utils.logutils.formatters import CustomFormatter


def test_logger_exports():
    """Test that the logutils module exports the expected symbols."""
    # Check that the module exports the standard logutils module
    # The logger_logging is not the same as the standard logutils module,
    # but it should provide the same functionality
    assert hasattr(logger_logging, 'getLogger')
    assert callable(logger_logging.getLogger)

    # Check that the CustomFormatter class is available from the src.logutils module
    from utils.logutils import CustomFormatter as exported_formatter
    assert exported_formatter == CustomFormatter


def test_logger_backward_compatibility():
    """Test backward compatibility with code that imports from the original module."""
    # Test that code that imports logutils from src.logutils still works

    # Create a logutils and log a message
    logger = original_logging.getLogger("test_backward_compatibility")

    # This should not raise any exceptions
    with mock.patch("logutils.Logger.info") as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")
