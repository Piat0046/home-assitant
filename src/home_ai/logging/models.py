"""Database models for logging."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestLog(BaseModel):
    """Model for request logs stored in PostgreSQL."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: UUID
    user_id: str | None = None
    input_type: str  # 'text' or 'audio'
    input_text: str | None = None
    output_text: str | None = None
    iot_commands: list[dict[str, Any]] | None = None
    duration_ms: int
    level: str = "INFO"


class ErrorLog(BaseModel):
    """Model for error logs stored in PostgreSQL."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: UUID | None = None
    error_type: str
    error_message: str
    stack_trace: str | None = None

