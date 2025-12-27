# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Centralized Logging Infrastructure

Provides structured logging for all Nexflow modules with:
- Consistent formatting across the codebase
- Context tracking for compilation phases
- Level-based filtering (DEBUG, INFO, WARNING, ERROR)
- Optional structured output for production environments

Usage:
    from backend.common.logging import get_logger

    LOG = get_logger(__name__)
    LOG.info("Compiling process", process=name)
    LOG.error("Parse failed", error=str(e), file=path)
"""

import logging
import sys
from typing import Optional, Any, Dict
from functools import lru_cache


# Default format for development
DEV_FORMAT = "%(levelname)s | %(name)s | %(message)s"

# Detailed format with timestamps for production
PROD_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class NexflowLogger(logging.Logger):
    """Extended logger with structured context support."""

    def _log_with_context(
        self,
        level: int,
        msg: str,
        args: tuple,
        exc_info: Any = None,
        extra: Optional[Dict] = None,
        **kwargs: Any
    ) -> None:
        """Log with additional context fields."""
        if kwargs:
            # Append context to message
            context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            msg = f"{msg} [{context_str}]"
        super()._log(level, msg, args, exc_info=exc_info, extra=extra)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message with optional context."""
        if self.isEnabledFor(logging.DEBUG):
            self._log_with_context(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message with optional context."""
        if self.isEnabledFor(logging.INFO):
            self._log_with_context(logging.INFO, msg, args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message with optional context."""
        if self.isEnabledFor(logging.WARNING):
            self._log_with_context(logging.WARNING, msg, args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message with optional context."""
        if self.isEnabledFor(logging.ERROR):
            self._log_with_context(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message with optional context."""
        if self.isEnabledFor(logging.CRITICAL):
            self._log_with_context(logging.CRITICAL, msg, args, **kwargs)


# Set custom logger class
logging.setLoggerClass(NexflowLogger)


@lru_cache(maxsize=128)
def get_logger(name: str) -> NexflowLogger:
    """Get a logger for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured NexflowLogger instance
    """
    logger = logging.getLogger(name)
    return logger


def configure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    stream: Any = None,
    production: bool = False
) -> None:
    """Configure the root logger for Nexflow.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        stream: Output stream (default: stderr)
        production: Use production format with timestamps
    """
    if format_string is None:
        format_string = PROD_FORMAT if production else DEV_FORMAT

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(logging.Formatter(format_string, DATE_FORMAT))

    # Configure root backend logger
    root_logger = logging.getLogger("backend")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    root_logger.propagate = False


def set_level(level: int) -> None:
    """Set logging level for all backend loggers.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger("backend").setLevel(level)


# Convenience aliases
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
