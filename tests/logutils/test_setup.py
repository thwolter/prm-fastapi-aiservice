"""Tests for the setup module."""
import logging
from unittest import mock

from src.utils.logutils.setup import setup_logging, get_logger


def test_setup_logging():
    """Test setting up logutils."""
    with mock.patch("src.utils.logutils.setup.configure_root_logger") as mock_configure:
        setup_logging()
        mock_configure.assert_called_once()


def test_get_logger():
    """Test getting a logutils."""
    with mock.patch("src.utils.logutils.setup.logging.getLogger") as mock_get_logger:
        mock_logger = mock.MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = get_logger("test_name")

        mock_get_logger.assert_called_once_with("test_name")
        assert logger == mock_logger


def test_get_logger_integration():
    """Test getting a logutils (integration test)."""
    # This is a simple integration test to ensure that get_logger
    # returns a real logutils instance with the correct name
    logger = get_logger("test_integration")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_integration"
