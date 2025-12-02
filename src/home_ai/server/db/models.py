"""SQLAlchemy database models for logging."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RequestLogDB(Base):
    """SQLAlchemy model for request logs."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    request_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=True)
    input_type = Column(String(50), nullable=False)
    input_text = Column(Text, nullable=True)
    output_text = Column(Text, nullable=True)
    iot_commands = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=False)
    level = Column(String(20), default="INFO", nullable=False)


class ErrorLogDB(Base):
    """SQLAlchemy model for error logs."""

    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    request_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    error_type = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
