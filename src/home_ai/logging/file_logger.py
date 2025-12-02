"""File-based logging implementation."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class FileLogger:
    """File logger with daily rotation.

    Creates log files with date-based naming and automatic rotation.
    """

    def __init__(
        self,
        log_dir: str = "./logs",
        name: str = "app",
        level: str = "INFO",
        format_string: str | None = None,
    ):
        """Initialize file logger.

        Args:
            log_dir: Directory to store log files.
            name: Logger name and filename prefix.
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            format_string: Custom log format string.
        """
        self.log_dir = Path(log_dir)
        self.name = name
        self.level = getattr(logging, level.upper(), logging.INFO)

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self._logger = logging.getLogger(f"home_ai.{name}")
        self._logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()

        # Create file handler with daily rotation
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{name}-{today}.log"

        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(self.level)

        # Set format
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        self._logger.addHandler(handler)

    def _format_extra(self, extra: dict[str, Any] | None) -> str:
        """Format extra data for logging."""
        if extra:
            return " | " + " ".join(f"{k}={v}" for k, v in extra.items())
        return ""

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log debug message."""
        self._logger.debug(message + self._format_extra(extra))

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log info message."""
        self._logger.info(message + self._format_extra(extra))

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log warning message."""
        self._logger.warning(message + self._format_extra(extra))

    def error(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log error message."""
        self._logger.error(message + self._format_extra(extra))

    def critical(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log critical message."""
        self._logger.critical(message + self._format_extra(extra))


def get_client_logger(log_dir: str = "./logs/client") -> FileLogger:
    """Get a file logger configured for client use.

    Args:
        log_dir: Directory to store client log files.

    Returns:
        FileLogger instance configured for client.
    """
    return FileLogger(log_dir=log_dir, name="client", level="INFO")


def get_server_debug_logger(log_dir: str = "./logs/server") -> FileLogger:
    """Get a file logger configured for server debug logging.

    Args:
        log_dir: Directory to store server log files.

    Returns:
        FileLogger instance configured for server debugging.
    """
    return FileLogger(log_dir=log_dir, name="debug", level="DEBUG")
