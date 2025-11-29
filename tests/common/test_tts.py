"""Tests for TTS implementations - TDD: Write tests first."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestGTTS:
    """Tests for gTTS implementation."""

    def test_gtts_implements_interface(self):
        """GTTSImpl should implement TTSInterface."""
        from home_ai.common.tts.gtts_impl import GTTSImpl
        from home_ai.common.interfaces import TTSInterface
        
        tts = GTTSImpl()
        assert hasattr(tts, 'synthesize')
        assert hasattr(tts, 'synthesize_async')
        assert hasattr(tts, 'speak')
    
    def test_gtts_synthesize_returns_bytes(self):
        """GTTSImpl.synthesize should return bytes."""
        from home_ai.common.tts.gtts_impl import GTTSImpl
        
        tts = GTTSImpl()
        
        with patch('home_ai.common.tts.gtts_impl.gTTS') as mock_gtts:
            mock_instance = MagicMock()
            mock_instance.write_to_fp = MagicMock(side_effect=lambda fp: fp.write(b"audio_data"))
            mock_gtts.return_value = mock_instance
            
            result = tts.synthesize("테스트 텍스트")
            
            assert isinstance(result, bytes)
    
    @pytest.mark.asyncio
    async def test_gtts_synthesize_async(self):
        """GTTSImpl.synthesize_async should work asynchronously."""
        from home_ai.common.tts.gtts_impl import GTTSImpl
        
        tts = GTTSImpl()
        
        with patch('home_ai.common.tts.gtts_impl.gTTS') as mock_gtts:
            mock_instance = MagicMock()
            mock_instance.write_to_fp = MagicMock(side_effect=lambda fp: fp.write(b"audio_data"))
            mock_gtts.return_value = mock_instance
            
            result = await tts.synthesize_async("테스트 텍스트")
            
            assert isinstance(result, bytes)
    
    def test_gtts_uses_korean_language(self):
        """GTTSImpl should default to Korean language."""
        from home_ai.common.tts.gtts_impl import GTTSImpl
        
        tts = GTTSImpl()
        
        assert tts.lang == "ko"
    
    def test_gtts_custom_language(self):
        """GTTSImpl should accept custom language."""
        from home_ai.common.tts.gtts_impl import GTTSImpl
        
        tts = GTTSImpl(lang="en")
        
        assert tts.lang == "en"


class TestOpenAITTS:
    """Tests for OpenAI TTS API implementation."""

    def test_openai_tts_implements_interface(self):
        """OpenAITTS should implement TTSInterface."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        from home_ai.common.interfaces import TTSInterface
        
        tts = OpenAITTS(api_key="test_key")
        assert hasattr(tts, 'synthesize')
        assert hasattr(tts, 'synthesize_async')
        assert hasattr(tts, 'speak')
    
    def test_openai_tts_synthesize_returns_bytes(self):
        """OpenAITTS.synthesize should return bytes."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        
        tts = OpenAITTS(api_key="test_key")
        
        with patch.object(tts, '_client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = b"audio_data"
            mock_client.audio.speech.create.return_value = mock_response
            
            result = tts.synthesize("테스트 텍스트")
            
            assert isinstance(result, bytes)
    
    @pytest.mark.asyncio
    async def test_openai_tts_synthesize_async(self):
        """OpenAITTS.synthesize_async should work asynchronously."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        
        tts = OpenAITTS(api_key="test_key")
        
        with patch.object(tts, '_async_client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = b"audio_data"
            mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
            
            result = await tts.synthesize_async("테스트 텍스트")
            
            assert isinstance(result, bytes)
    
    def test_openai_tts_default_voice(self):
        """OpenAITTS should have default voice."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        
        tts = OpenAITTS(api_key="test_key")
        
        assert tts.voice == "alloy"
    
    def test_openai_tts_custom_voice(self):
        """OpenAITTS should accept custom voice."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        
        tts = OpenAITTS(api_key="test_key", voice="nova")
        
        assert tts.voice == "nova"
    
    def test_openai_tts_default_model(self):
        """OpenAITTS should use tts-1 model by default."""
        from home_ai.common.tts.openai_tts import OpenAITTS
        
        tts = OpenAITTS(api_key="test_key")
        
        assert tts.model == "tts-1"

