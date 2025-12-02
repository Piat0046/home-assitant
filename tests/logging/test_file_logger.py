"""Tests for file logger - TDD: Write tests first."""

from datetime import datetime


class TestFileLogger:
    """Tests for FileLogger implementation."""

    def test_file_logger_creates_log_directory(self, tmp_path):
        """FileLogger should create log directory if it doesn't exist."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs" / "test"
        logger = FileLogger(log_dir=str(log_dir), name="test")

        assert log_dir.exists()

    def test_file_logger_creates_log_file(self, tmp_path):
        """FileLogger should create a log file."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.info("Test message")

        # Check that at least one log file exists
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) >= 1

    def test_file_logger_writes_info(self, tmp_path):
        """FileLogger should write INFO level messages."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.info("Test info message")

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        assert "Test info message" in content
        assert "INFO" in content

    def test_file_logger_writes_error(self, tmp_path):
        """FileLogger should write ERROR level messages."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.error("Test error message")

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        assert "Test error message" in content
        assert "ERROR" in content

    def test_file_logger_writes_debug(self, tmp_path):
        """FileLogger should write DEBUG level messages when level is DEBUG."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test", level="DEBUG")
        logger.debug("Test debug message")

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        assert "Test debug message" in content
        assert "DEBUG" in content

    def test_file_logger_writes_warning(self, tmp_path):
        """FileLogger should write WARNING level messages."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.warning("Test warning message")

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        assert "Test warning message" in content
        assert "WARNING" in content

    def test_file_logger_includes_timestamp(self, tmp_path):
        """FileLogger should include timestamp in log entries."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.info("Test message with timestamp")

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        # Check for date pattern (YYYY-MM-DD)
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content

    def test_file_logger_log_with_extra_data(self, tmp_path):
        """FileLogger should support logging with extra data."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.info("Request processed", extra={"request_id": "123", "duration_ms": 50})

        log_file = list(log_dir.glob("*.log"))[0]
        content = log_file.read_text()

        assert "Request processed" in content

    def test_file_logger_daily_rotation_filename(self, tmp_path):
        """FileLogger should use date-based filename for rotation."""
        from home_ai.logging.file_logger import FileLogger

        log_dir = tmp_path / "logs"
        logger = FileLogger(log_dir=str(log_dir), name="test")
        logger.info("Test message")

        today = datetime.now().strftime("%Y-%m-%d")
        log_files = list(log_dir.glob(f"*{today}*.log"))
        assert len(log_files) >= 1


class TestClientLogger:
    """Tests for client-specific file logger."""

    def test_client_logger_uses_client_prefix(self, tmp_path):
        """Client logger should use 'client' prefix in filename."""
        from home_ai.logging.file_logger import get_client_logger

        log_dir = tmp_path / "logs" / "client"
        logger = get_client_logger(log_dir=str(log_dir))
        logger.info("Client log message")

        log_files = list(log_dir.glob("client*.log"))
        assert len(log_files) >= 1


class TestServerLogger:
    """Tests for server-specific file logger."""

    def test_server_logger_uses_debug_prefix(self, tmp_path):
        """Server debug logger should use 'debug' prefix in filename."""
        from home_ai.logging.file_logger import get_server_debug_logger

        log_dir = tmp_path / "logs" / "server"
        logger = get_server_debug_logger(log_dir=str(log_dir))
        logger.info("Server debug log message")

        log_files = list(log_dir.glob("debug*.log"))
        assert len(log_files) >= 1
