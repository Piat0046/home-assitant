"""Tests for database module - TDD: Write tests first."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestDatabaseConnection:
    """Tests for database connection."""

    def test_database_url_config(self):
        """Database URL should be configurable."""
        from home_ai.server.db.connection import get_database_url
        
        url = get_database_url()
        assert "postgresql" in url
    
    def test_engine_creation(self):
        """Engine should be creatable from config."""
        from home_ai.server.db.connection import create_async_engine_instance
        
        # Use async engine since we have asyncpg installed
        engine = create_async_engine_instance("postgresql+asyncpg://test:test@localhost/test")
        assert engine is not None


class TestDatabaseModels:
    """Tests for SQLAlchemy database models."""

    def test_request_log_table_exists(self):
        """RequestLog table should be defined."""
        from home_ai.server.db.models import RequestLogDB
        
        assert hasattr(RequestLogDB, '__tablename__')
        assert RequestLogDB.__tablename__ == "request_logs"
    
    def test_error_log_table_exists(self):
        """ErrorLog table should be defined."""
        from home_ai.server.db.models import ErrorLogDB
        
        assert hasattr(ErrorLogDB, '__tablename__')
        assert ErrorLogDB.__tablename__ == "error_logs"
    
    def test_request_log_has_required_columns(self):
        """RequestLog should have required columns."""
        from home_ai.server.db.models import RequestLogDB
        
        columns = [c.name for c in RequestLogDB.__table__.columns]
        
        assert "id" in columns
        assert "timestamp" in columns
        assert "request_id" in columns
        assert "input_type" in columns
        assert "input_text" in columns
        assert "output_text" in columns
        assert "duration_ms" in columns
    
    def test_error_log_has_required_columns(self):
        """ErrorLog should have required columns."""
        from home_ai.server.db.models import ErrorLogDB
        
        columns = [c.name for c in ErrorLogDB.__table__.columns]
        
        assert "id" in columns
        assert "timestamp" in columns
        assert "error_type" in columns
        assert "error_message" in columns
        assert "stack_trace" in columns

