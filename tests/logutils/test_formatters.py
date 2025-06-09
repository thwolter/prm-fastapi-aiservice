"""Tests for the formatters module."""
import logging as logutils

from src.utils.logutils.formatters import CustomFormatter, create_default_formatter


class TestCustomFormatter:
    """Tests for the CustomFormatter class."""

    def test_format_info(self):
        """Test formatting an INFO level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=logutils.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "INFO:    : Test message" in formatted

    def test_format_debug(self):
        """Test formatting a DEBUG level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=logutils.DEBUG,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "DEBUG:   : Test message" in formatted

    def test_format_warning(self):
        """Test formatting a WARNING level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=logutils.WARNING,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "WARNING: : Test message" in formatted

    def test_format_error(self):
        """Test formatting an ERROR level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=logutils.ERROR,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "ERROR:   : Test message" in formatted

    def test_format_critical(self):
        """Test formatting a CRITICAL level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=logutils.CRITICAL,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "CRITICAL:: Test message" in formatted

    def test_format_custom_level(self):
        """Test formatting a custom level record."""
        formatter = CustomFormatter('%(levelname)s: %(message)s')
        record = logutils.LogRecord(
            name="test",
            level=25,  # Custom level between INFO and WARNING
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Set a custom level name
        record.levelname = "Level 25"

        formatted = formatter.format(record)

        # For custom levels, the levelname should be included in the output
        assert "Level 25: Test message" in formatted


def test_create_default_formatter():
    """Test creating the default formatter."""
    formatter = create_default_formatter()

    assert isinstance(formatter, CustomFormatter)
    assert formatter._fmt == '%(levelname)s [%(name)s] %(message)s'
