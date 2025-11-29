"""Database logging implementation for PostgreSQL."""

from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from home_ai.logging.models import RequestLog, ErrorLog


class DatabaseLogger:
    """Logger that writes to PostgreSQL database.
    
    Used for server-side logging of requests and errors.
    """
    
    def __init__(self, session_factory: Callable):
        """Initialize database logger.
        
        Args:
            session_factory: Callable that returns a database session.
        """
        self._session_factory = session_factory
    
    def log_request(
        self,
        request_id: UUID,
        input_type: str,
        input_text: str,
        output_text: str,
        duration_ms: int,
        user_id: str | None = None,
        iot_commands: list[dict[str, Any]] | None = None,
        level: str = "INFO",
    ) -> None:
        """Log a request to the database.
        
        Args:
            request_id: Unique identifier for the request.
            input_type: Type of input ('text' or 'audio').
            input_text: The input text (transcribed if audio).
            output_text: The response text.
            duration_ms: Request processing duration in milliseconds.
            user_id: Optional user identifier.
            iot_commands: List of IoT commands executed.
            level: Log level.
        """
        session = self._session_factory()
        try:
            log_entry = RequestLog(
                request_id=request_id,
                user_id=user_id,
                input_type=input_type,
                input_text=input_text,
                output_text=output_text,
                iot_commands=iot_commands,
                duration_ms=duration_ms,
                level=level,
            )
            session.add(log_entry)
            session.commit()
        finally:
            session.close()
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str | None = None,
        request_id: UUID | None = None,
    ) -> None:
        """Log an error to the database.
        
        Args:
            error_type: Type/class of the error.
            error_message: Error message.
            stack_trace: Full stack trace.
            request_id: Optional request ID if error occurred during request.
        """
        session = self._session_factory()
        try:
            log_entry = ErrorLog(
                request_id=request_id,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
            )
            session.add(log_entry)
            session.commit()
        finally:
            session.close()

