"""
Logging package for the application.

This package provides utilities for configuring and using logutils
in a consistent way throughout the application.

It re-exports the standard logutils module for backward compatibility.
"""
# Import the standard logutils module first to avoid circular imports
import logging

# Re-export the standard logutils module for backward compatibility
# This allows code that imports from src.core.logutils to continue working
__all__ = [
    'logging',
    'CustomFormatter',
    'create_default_formatter',
    'get_log_level',
    'create_console_handler',
    'configure_root_logger',
    'setup_logging',
    'get_logger',
]

# Now import the rest of the modules
from src.utils.logutils.formatters import CustomFormatter, create_default_formatter
from src.utils.logutils.config import (
    get_log_level,
    create_console_handler,
    configure_root_logger,
)
from src.utils.logutils.setup import setup_logging, get_logger

# Set up logutils when the package is imported
setup_logging()
