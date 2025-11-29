"""Tests for data models - TDD: Write tests first."""

import pytest
from pydantic import ValidationError


class TestIoTCommand:
    """Tests for IoTCommand model."""

    def test_iot_command_creation(self):
        """IoTCommand should be created with required fields."""
        from home_ai.common.models import IoTCommand
        
        cmd = IoTCommand(device="light", action="on")
        assert cmd.device == "light"
        assert cmd.action == "on"
        assert cmd.parameters == {}
    
    def test_iot_command_with_parameters(self):
        """IoTCommand should accept parameters."""
        from home_ai.common.models import IoTCommand
        
        cmd = IoTCommand(
            device="light",
            action="set_brightness",
            parameters={"brightness": 50, "room": "living_room"}
        )
        assert cmd.parameters["brightness"] == 50
        assert cmd.parameters["room"] == "living_room"
    
    def test_iot_command_requires_device(self):
        """IoTCommand should require device field."""
        from home_ai.common.models import IoTCommand
        
        with pytest.raises(ValidationError):
            IoTCommand(action="on")
    
    def test_iot_command_requires_action(self):
        """IoTCommand should require action field."""
        from home_ai.common.models import IoTCommand
        
        with pytest.raises(ValidationError):
            IoTCommand(device="light")


class TestIoTResult:
    """Tests for IoTResult model."""

    def test_iot_result_creation(self):
        """IoTResult should be created with required fields."""
        from home_ai.common.models import IoTResult
        
        result = IoTResult(success=True, message="Light turned on")
        assert result.success is True
        assert result.message == "Light turned on"
        assert result.data == {}
    
    def test_iot_result_with_data(self):
        """IoTResult should accept additional data."""
        from home_ai.common.models import IoTResult
        
        result = IoTResult(
            success=True,
            message="Light turned on",
            data={"new_state": "on", "brightness": 100}
        )
        assert result.data["new_state"] == "on"


class TestLLMResponse:
    """Tests for LLMResponse model."""

    def test_llm_response_creation(self):
        """LLMResponse should be created with text."""
        from home_ai.common.models import LLMResponse
        
        response = LLMResponse(text="거실 조명을 켰습니다.")
        assert response.text == "거실 조명을 켰습니다."
        assert response.commands == []
    
    def test_llm_response_with_commands(self):
        """LLMResponse should accept IoT commands."""
        from home_ai.common.models import LLMResponse, IoTCommand
        
        response = LLMResponse(
            text="거실 조명을 켰습니다.",
            commands=[
                IoTCommand(device="light", action="on", parameters={"room": "living_room"})
            ]
        )
        assert len(response.commands) == 1
        assert response.commands[0].device == "light"


class TestChatRequest:
    """Tests for ChatRequest model."""

    def test_chat_request_text_mode(self):
        """ChatRequest should work in text mode."""
        from home_ai.common.models import ChatRequest
        
        request = ChatRequest(text="불 켜줘", mode="text")
        assert request.text == "불 켜줘"
        assert request.mode == "text"
        assert request.audio is None
    
    def test_chat_request_audio_mode(self):
        """ChatRequest should work in audio mode."""
        from home_ai.common.models import ChatRequest
        
        request = ChatRequest(audio=b"audio_data", mode="audio")
        assert request.audio == b"audio_data"
        assert request.mode == "audio"
    
    def test_chat_request_default_mode(self):
        """ChatRequest should default to text mode."""
        from home_ai.common.models import ChatRequest
        
        request = ChatRequest(text="불 켜줘")
        assert request.mode == "text"


class TestChatResponse:
    """Tests for ChatResponse model."""

    def test_chat_response_creation(self):
        """ChatResponse should be created with text."""
        from home_ai.common.models import ChatResponse
        
        response = ChatResponse(text="조명을 켰습니다.")
        assert response.text == "조명을 켰습니다."
        assert response.audio is None
        assert response.commands_executed == []
    
    def test_chat_response_with_audio(self):
        """ChatResponse should include audio when provided."""
        from home_ai.common.models import ChatResponse
        
        response = ChatResponse(text="조명을 켰습니다.", audio=b"audio_response")
        assert response.audio == b"audio_response"
    
    def test_chat_response_with_executed_commands(self):
        """ChatResponse should include executed command results."""
        from home_ai.common.models import ChatResponse, IoTResult
        
        response = ChatResponse(
            text="조명을 켰습니다.",
            commands_executed=[
                IoTResult(success=True, message="Light turned on")
            ]
        )
        assert len(response.commands_executed) == 1
        assert response.commands_executed[0].success is True


class TestConfig:
    """Tests for configuration classes."""

    def test_settings_from_env(self):
        """Settings should be loadable from environment variables."""
        from home_ai.common.config import Settings
        
        settings = Settings()
        assert hasattr(settings, 'server_host')
        assert hasattr(settings, 'server_port')
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'stt_provider')
        assert hasattr(settings, 'tts_provider')
        assert hasattr(settings, 'llm_provider')

