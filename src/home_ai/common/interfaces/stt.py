"""Speech-to-Text interface protocol."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class STTInterface(Protocol):
    """Protocol for Speech-to-Text implementations.
    
    All STT implementations should conform to this interface.
    Supports both synchronous and asynchronous transcription.
    """
    
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes to transcribe.
            
        Returns:
            Transcribed text string.
        """
        ...
    
    async def transcribe_async(self, audio_data: bytes) -> str:
        """Asynchronously transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes to transcribe.
            
        Returns:
            Transcribed text string.
        """
        ...

