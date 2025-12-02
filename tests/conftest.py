"""Pytest configuration and shared fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest

# ============================================================================
# Mock Fixtures for STT
# ============================================================================


@pytest.fixture
def mock_audio_data() -> bytes:
    """Generate mock audio data for testing."""
    import io
    import wave

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)  # 1 second of silence
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def mock_stt():
    """Mock STT interface."""
    mock = MagicMock()
    mock.transcribe = MagicMock(return_value="테스트 음성 입력")
    mock.transcribe_async = AsyncMock(return_value="테스트 음성 입력")
    return mock


# ============================================================================
# Mock Fixtures for TTS
# ============================================================================


@pytest.fixture
def mock_tts():
    """Mock TTS interface."""
    mock = MagicMock()
    mock.speak = MagicMock()
    mock.speak_async = AsyncMock()
    mock.synthesize = MagicMock(return_value=b"audio_data")
    mock.synthesize_async = AsyncMock(return_value=b"audio_data")
    return mock


# ============================================================================
# Mock Fixtures for LLM
# ============================================================================


@pytest.fixture
def mock_llm():
    """Mock LLM interface."""
    from home_ai.common.models import IoTCommand, LLMResponse

    mock = MagicMock()
    mock_response = LLMResponse(
        text="거실 조명을 켰습니다.",
        commands=[IoTCommand(device="light", action="on", parameters={"room": "living_room"})],
    )
    mock.process = MagicMock(return_value=mock_response)
    mock.process_async = AsyncMock(return_value=mock_response)
    return mock


# ============================================================================
# Mock Fixtures for IoT Devices
# ============================================================================


@pytest.fixture
def mock_iot_device():
    """Mock IoT device interface."""
    from home_ai.common.models import IoTResult

    mock = MagicMock()
    mock.execute = MagicMock(return_value=IoTResult(success=True, message="Command executed"))
    mock.execute_async = AsyncMock(return_value=IoTResult(success=True, message="Command executed"))
    mock.get_state = MagicMock(return_value={"power": "on", "brightness": 100})
    return mock


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


# ============================================================================
# API Client Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client():
    """Mock API client."""
    from home_ai.client.api_client import RESTClient

    mock = MagicMock(spec=RESTClient)
    mock.chat_async = AsyncMock(return_value={"text": "테스트 응답", "commands_executed": [], "request_id": "test-123"})
    mock.get_devices_async = AsyncMock(return_value={"lights": {}, "alarm": {}, "thermostat": {}})
    return mock


# ============================================================================
# Integration Test Markers
# ============================================================================


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
