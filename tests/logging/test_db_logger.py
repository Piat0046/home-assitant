"""Tests for database logger - TDD: Write tests first."""

from uuid import uuid4


class TestDBLogger:
    """Tests for DatabaseLogger implementation."""

    def test_db_logger_log_request(self):
        """DBLogger should log requests to database."""
        from home_ai.logging.db_logger import DatabaseLogger

        # Create mock session
        logs = []

        class MockSession:
            def add(self, obj):
                logs.append(obj)

            def commit(self):
                pass

            def close(self):
                pass

        logger = DatabaseLogger(session_factory=lambda: MockSession())

        request_id = uuid4()
        logger.log_request(
            request_id=request_id,
            input_type="text",
            input_text="불 켜줘",
            output_text="거실 조명을 켰습니다.",
            duration_ms=150,
        )

        assert len(logs) == 1
        assert logs[0].request_id == request_id
        assert logs[0].input_type == "text"
        assert logs[0].input_text == "불 켜줘"

    def test_db_logger_log_error(self):
        """DBLogger should log errors to database."""
        from home_ai.logging.db_logger import DatabaseLogger

        logs = []

        class MockSession:
            def add(self, obj):
                logs.append(obj)

            def commit(self):
                pass

            def close(self):
                pass

        logger = DatabaseLogger(session_factory=lambda: MockSession())

        request_id = uuid4()
        logger.log_error(
            request_id=request_id, error_type="ValueError", error_message="Invalid input", stack_trace="Traceback..."
        )

        assert len(logs) == 1
        assert logs[0].request_id == request_id
        assert logs[0].error_type == "ValueError"

    def test_db_logger_log_iot_commands(self):
        """DBLogger should log IoT commands in request log."""
        from home_ai.logging.db_logger import DatabaseLogger

        logs = []

        class MockSession:
            def add(self, obj):
                logs.append(obj)

            def commit(self):
                pass

            def close(self):
                pass

        logger = DatabaseLogger(session_factory=lambda: MockSession())

        iot_commands = [{"device": "light", "action": "on", "parameters": {"room": "living_room"}}]

        logger.log_request(
            request_id=uuid4(),
            input_type="text",
            input_text="불 켜줘",
            output_text="켰습니다",
            iot_commands=iot_commands,
            duration_ms=100,
        )

        assert logs[0].iot_commands == iot_commands


class TestLogModels:
    """Tests for log database models."""

    def test_request_log_model_creation(self):
        """RequestLog model should be creatable."""
        from home_ai.logging.models import RequestLog

        log = RequestLog(
            request_id=uuid4(),
            input_type="text",
            input_text="Test input",
            output_text="Test output",
            duration_ms=100,
            level="INFO",
        )

        assert log.input_type == "text"
        assert log.duration_ms == 100

    def test_error_log_model_creation(self):
        """ErrorLog model should be creatable."""
        from home_ai.logging.models import ErrorLog

        log = ErrorLog(
            request_id=uuid4(),
            error_type="TestError",
            error_message="Test error message",
            stack_trace="Test stack trace",
        )

        assert log.error_type == "TestError"

    def test_request_log_has_timestamp(self):
        """RequestLog should have timestamp field."""
        from home_ai.logging.models import RequestLog

        log = RequestLog(
            request_id=uuid4(), input_type="text", input_text="Test", output_text="Test", duration_ms=100, level="INFO"
        )

        assert hasattr(log, "timestamp")

    def test_error_log_has_timestamp(self):
        """ErrorLog should have timestamp field."""
        from home_ai.logging.models import ErrorLog

        log = ErrorLog(request_id=uuid4(), error_type="TestError", error_message="Test error", stack_trace="")

        assert hasattr(log, "timestamp")
