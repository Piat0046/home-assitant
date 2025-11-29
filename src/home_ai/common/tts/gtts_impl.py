"""gTTS (Google Text-to-Speech) implementation."""

import asyncio
import io
import tempfile
from typing import Optional

from gtts import gTTS


class GTTSImpl:
    """Text-to-Speech using gTTS (Google Text-to-Speech).
    
    Uses the free Google TTS service.
    Requires internet connection.
    """
    
    def __init__(self, lang: str = "ko"):
        """Initialize gTTS.
        
        Args:
            lang: Language code for synthesis (default: Korean).
        """
        self.lang = lang
    
    def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes.
        
        Args:
            text: Text to convert to speech.
            
        Returns:
            Audio bytes in MP3 format.
        """
        tts = gTTS(text=text, lang=self.lang)
        
        # Write to BytesIO
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.read()
    
    async def synthesize_async(self, text: str) -> bytes:
        """Asynchronously synthesize text to audio bytes.
        
        Args:
            text: Text to convert to speech.
            
        Returns:
            Audio bytes in MP3 format.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.synthesize, text)
    
    def speak(self, text: str) -> None:
        """Synthesize and immediately play audio.
        
        Args:
            text: Text to speak.
        """
        import pygame
        
        audio_data = self.synthesize(text)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load and play audio
        audio_buffer = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

