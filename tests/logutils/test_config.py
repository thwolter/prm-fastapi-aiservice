"""Tests for the config module."""
import logging as logutils
import sys
from unittest import mock

from src.utils.logutils.config import (
    get_log_level,
    create_console_handler,
    configure_root_logger,
)


def test_get_log_level():
    """Test getting the log level from settings."""
    with mock.patch("src.utils.logutils.config.settings") as mock_settings:
        # Test with a valid log level
        mock_settings.LOG_LEVEL = "DEBUG"
        assert get_log_level() == logutils.DEBUG

        # Test with a valid log level in lowercase
        mock_settings.LOG_LEVEL = "info"
        assert get_log_level() == logutils.INFO

        # Test with an invalid log level (should default to INFO)
        mock_settings.LOG_LEVEL = "INVALID"
        assert get_log_level() == logutils.INFO


def test_create_console_handler():
    """Test creating a console handler."""
    # Test with default stream (stdout)
    handler = create_console_handler()
    assert isinstance(handler, logutils.StreamHandler)
    assert handler.stream == sys.stdout

    # Test with custom stream
    custom_stream = mock.MagicMock()
    handler = create_console_handler(custom_stream)
    assert isinstance(handler, logutils.StreamHandler)
    assert handler.stream == custom_stream


def test_configure_root_logger():
    """Test configuring the root logutils."""
    # Save the original root logutils configuration
    original_level = logutils.root.level
    original_handlers = logutils.root.handlers.copy()

    try:
        # Clear the root logutils
        logutils.root.handlers.clear()

        # Test with default parameters
        with mock.patch("src.utils.logutils.config.get_log_level") as mock_get_log_level:
            mock_get_log_level.return_value = logutils.WARNING
            configure_root_logger()

            # Check that the root logutils was configured correctly
            assert logutils.root.level == logutils.WARNING
            assert len(logutils.root.handlers) == 1
            assert isinstance(logutils.root.handlers[0], logutils.StreamHandler)
            assert logutils.root.handlers[0].formatter is not None

        # Clear the root logutils again
        logutils.root.handlers.clear()

        # Test with custom parameters
        custom_level = logutils.DEBUG
        custom_handler = logutils.StreamHandler(sys.stderr)
        custom_formatter = logutils.Formatter("%(message)s")

        configure_root_logger(
            level=custom_level,
            handlers=[custom_handler],
            formatter=custom_formatter,
        )

        # Check that the root logutils was configured correctly
        assert logutils.root.level == custom_level
        assert len(logutils.root.handlers) == 1
        assert logutils.root.handlers[0] == custom_handler
        assert logutils.root.handlers[0].formatter == custom_formatter

    finally:
        # Restore the original root logutils configuration
        logutils.root.level = original_level
        logutils.root.handlers.clear()
        for handler in original_handlers:
            logutils.root.addHandler(handler)
