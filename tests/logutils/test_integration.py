"""Integration tests for the logutils package."""

import io
import logging

from src.utils.logutils import (
    CustomFormatter,
    configure_root_logger,
    create_console_handler,
    create_default_formatter,
    get_log_level,
    get_logger,
    setup_logging,
)


def test_package_exports():
    """Test that the package exports the expected symbols."""
    # Check that the package exports the standard logutils module
    from src.utils import logutils
    from src.utils import logutils as logging_module

    assert logging_module == logutils

    # Check that the package exports the expected functions and classes
    assert callable(CustomFormatter)
    assert callable(create_default_formatter)
    assert callable(get_log_level)
    assert callable(create_console_handler)
    assert callable(configure_root_logger)
    assert callable(setup_logging)
    assert callable(get_logger)


def test_logger_integration():
    """Test the integration of all logutils components."""
    # Save the original root logutils configuration
    original_level = logging.root.level
    original_handlers = logging.root.handlers.copy()

    try:
        # Clear the root logutils
        logging.root.handlers.clear()

        # Create a stream to capture log output
        stream = io.StringIO()

        # Configure logutils with a custom handler
        handler = logging.StreamHandler(stream)
        formatter = CustomFormatter('%(levelname)s [%(name)s] %(message)s')
        handler.setFormatter(formatter)

        configure_root_logger(
            level=logging.INFO,
            handlers=[handler],
        )

        # Get a logutils and log a message
        logger = get_logger('test_integration')
        logger.info('Test message')

        # Check that the message was logged correctly
        output = stream.getvalue()
        assert 'INFO:     [test_integration] Test message' in output

    finally:
        # Restore the original root logutils configuration
        logging.root.level = original_level
        logging.root.handlers.clear()
        for handler in original_handlers:
            logging.root.addHandler(handler)
