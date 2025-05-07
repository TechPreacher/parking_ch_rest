"""Logging utility functions."""

import logging
import sys

from ..config.settings import LogLevel, get_settings


def setup_logging(
    name: str = "parkings_ch_api",
    level: LogLevel | None = None,
) -> logging.Logger:
    """Set up and configure logging.

    Args:
        name: Logger name
        level: Log level (defaults to value from settings)

    Returns:
        logging.Logger: Configured logger
    """
    settings = get_settings()
    log_level = level or settings.log_level

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level.value)

    # Create console handler if logger doesn't have handlers yet
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level.value)

        # Create formatter
        formatter = logging.Formatter(settings.log_format)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger
