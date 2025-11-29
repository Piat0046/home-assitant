"""Tests for STT implementations - TDD: Write tests first."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestGoogleSTT:
    """Tests for Google Speech Recognition STT."""

    def test_google_stt_implements_interface(self):
        """GoogleSTT should implement STTInterface."""
        from home_ai.common.stt.google_stt import GoogleSTT
        from home_ai.common.interfaces import STTInterface
        
        stt = GoogleSTT()
        assert hasattr(stt, 'transcribe')
        assert hasattr(stt, 'transcribe_async')
    
    def test_google_stt_transcribe_returns_string(self):
        """GoogleSTT.transcribe should return a string."""
        from home_ai.common.stt.google_stt import GoogleSTT
        
        stt = GoogleSTT()
        
        # Mock the recognizer directly
        stt._recognizer = MagicMock()
        stt._recognizer.recognize_google.return_value = "테스트 음성"
        
        result = stt.transcribe(b"fake_audio_data")
        
        assert isinstance(result, str)
        assert result == "테스트 음성"
    
    @pytest.mark.asyncio
    async def test_google_stt_transcribe_async(self):
        """GoogleSTT.transcribe_async should work asynchronously."""
        from home_ai.common.stt.google_stt import GoogleSTT
        
        stt = GoogleSTT()
        
        # Mock the recognizer directly
        stt._recognizer = MagicMock()
        stt._recognizer.recognize_google.return_value = "비동기 테스트"
        
        result = await stt.transcribe_async(b"fake_audio_data")
        
        assert isinstance(result, str)
        assert result == "비동기 테스트"
    
    def test_google_stt_handles_recognition_error(self):
        """GoogleSTT should handle recognition errors gracefully."""
        from home_ai.common.stt.google_stt import GoogleSTT
        
        stt = GoogleSTT()
        stt._recognizer = MagicMock()
        stt._recognizer.recognize_google.side_effect = Exception("Recognition failed")
        
        with pytest.raises(Exception):
            stt.transcribe(b"fake_audio_data")
    
    def test_google_stt_default_language(self):
        """GoogleSTT should default to Korean language."""
        from home_ai.common.stt.google_stt import GoogleSTT
        
        stt = GoogleSTT()
        assert stt.language == "ko-KR"
    
    def test_google_stt_custom_language(self):
        """GoogleSTT should accept custom language."""
        from home_ai.common.stt.google_stt import GoogleSTT
        
        stt = GoogleSTT(language="en-US")
        assert stt.language == "en-US"


class TestOpenAISTT:
    """Tests for OpenAI Whisper API STT."""

    def test_openai_stt_implements_interface(self):
        """OpenAISTT should implement STTInterface."""
        from home_ai.common.stt.openai_stt import OpenAISTT
        from home_ai.common.interfaces import STTInterface
        
        stt = OpenAISTT(api_key="test_key")
        assert hasattr(stt, 'transcribe')
        assert hasattr(stt, 'transcribe_async')
    
    def test_openai_stt_transcribe_returns_string(self):
        """OpenAISTT.transcribe should return a string."""
        from home_ai.common.stt.openai_stt import OpenAISTT
        
        stt = OpenAISTT(api_key="test_key")
        
        mock_response = MagicMock()
        mock_response.text = "테스트 음성"
        stt._client = MagicMock()
        stt._client.audio.transcriptions.create.return_value = mock_response
        
        result = stt.transcribe(b"fake_audio_data")
        
        assert isinstance(result, str)
        assert result == "테스트 음성"
    
    @pytest.mark.asyncio
    async def test_openai_stt_transcribe_async(self):
        """OpenAISTT.transcribe_async should work asynchronously."""
        from home_ai.common.stt.openai_stt import OpenAISTT
        
        stt = OpenAISTT(api_key="test_key")
        
        mock_response = MagicMock()
        mock_response.text = "비동기 테스트"
        stt._async_client = MagicMock()
        stt._async_client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
        
        result = await stt.transcribe_async(b"fake_audio_data")
        
        assert isinstance(result, str)
    
    def test_openai_stt_uses_whisper_model(self):
        """OpenAISTT should use whisper-1 model by default."""
        from home_ai.common.stt.openai_stt import OpenAISTT
        
        stt = OpenAISTT(api_key="test_key")
        
        assert stt.model == "whisper-1"
    
    def test_openai_stt_custom_model(self):
        """OpenAISTT should accept custom model."""
        from home_ai.common.stt.openai_stt import OpenAISTT
        
        stt = OpenAISTT(api_key="test_key", model="whisper-custom")
        
        assert stt.model == "whisper-custom"
