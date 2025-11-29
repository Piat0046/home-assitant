"""Tests for client module - TDD: Write tests first."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestAPIClient:
    """Tests for API client."""

    def test_rest_client_creation(self):
        """REST client should be creatable."""
        from home_ai.client.api_client import RESTClient
        
        client = RESTClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_rest_client_chat_text(self):
        """REST client should send text chat requests."""
        from home_ai.client.api_client import RESTClient
        
        client = RESTClient(base_url="http://localhost:8000")
        
        with patch.object(client, '_client') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "text": "거실 조명을 켰습니다.",
                "commands_executed": [],
                "request_id": "123"
            }
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await client.chat_async("거실 불 켜줘")
            
            assert result["text"] == "거실 조명을 켰습니다."
    
    def test_websocket_client_creation(self):
        """WebSocket client should be creatable."""
        from home_ai.client.api_client import WebSocketClient
        
        client = WebSocketClient(url="ws://localhost:8000/ws")
        assert "ws://localhost:8000" in client.url


class TestAudioModule:
    """Tests for audio module."""

    def test_audio_recorder_creation(self):
        """AudioRecorder should be creatable."""
        from home_ai.client.audio import AudioRecorder
        
        recorder = AudioRecorder()
        assert recorder is not None
    
    def test_audio_player_creation(self):
        """AudioPlayer should be creatable."""
        from home_ai.client.audio import AudioPlayer
        
        player = AudioPlayer()
        assert player is not None
    
    def test_audio_recorder_has_record_method(self):
        """AudioRecorder should have record method."""
        from home_ai.client.audio import AudioRecorder
        
        recorder = AudioRecorder()
        assert hasattr(recorder, 'record')
        assert hasattr(recorder, 'record_async')
    
    def test_audio_player_has_play_method(self):
        """AudioPlayer should have play method."""
        from home_ai.client.audio import AudioPlayer
        
        player = AudioPlayer()
        assert hasattr(player, 'play')
        assert hasattr(player, 'play_async')


class TestClientAssistant:
    """Tests for client assistant."""

    def test_assistant_creation(self):
        """ClientAssistant should be creatable."""
        from home_ai.client.assistant import ClientAssistant
        
        assistant = ClientAssistant(server_url="http://localhost:8000")
        assert assistant is not None
    
    def test_assistant_has_text_mode(self):
        """ClientAssistant should support text mode."""
        from home_ai.client.assistant import ClientAssistant
        
        assistant = ClientAssistant(server_url="http://localhost:8000")
        assert hasattr(assistant, 'process_text')
    
    def test_assistant_has_audio_mode(self):
        """ClientAssistant should support audio mode."""
        from home_ai.client.assistant import ClientAssistant
        
        assistant = ClientAssistant(server_url="http://localhost:8000")
        assert hasattr(assistant, 'process_audio')
    
    @pytest.mark.asyncio
    async def test_assistant_process_text(self):
        """ClientAssistant should process text input."""
        from home_ai.client.assistant import ClientAssistant
        from home_ai.client.api_client import RESTClient
        
        assistant = ClientAssistant(server_url="http://localhost:8000")
        
        # Create a proper mock for RESTClient
        mock_client = MagicMock(spec=RESTClient)
        mock_client.chat_async = AsyncMock(return_value={
            "text": "거실 조명을 켰습니다.",
            "commands_executed": [],
            "request_id": "123"
        })
        assistant._api_client = mock_client
        
        result = await assistant.process_text("거실 불 켜줘")
        
        assert "조명" in result["text"] or "켰습니다" in result["text"]

