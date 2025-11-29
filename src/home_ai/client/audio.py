"""Audio input/output handling."""

import asyncio
import io
import wave
from typing import Optional


class AudioRecorder:
    """Records audio from microphone.
    
    Note: Requires pyaudio to be installed for actual recording.
    Falls back to mock implementation if not available.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
    ):
        """Initialize audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz.
            channels: Number of audio channels.
            chunk_size: Size of audio chunks.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._pyaudio = None
        self._stream = None
        
        try:
            import pyaudio
            self._pyaudio = pyaudio.PyAudio()
        except ImportError:
            pass
    
    def record(self, duration: float = 5.0) -> bytes:
        """Record audio for a specified duration.
        
        Args:
            duration: Recording duration in seconds.
            
        Returns:
            Audio bytes in WAV format.
        """
        if not self._pyaudio:
            # Return mock audio data if pyaudio not available
            return self._create_mock_audio(duration)
        
        import pyaudio
        
        stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        num_chunks = int(self.sample_rate / self.chunk_size * duration)
        
        for _ in range(num_chunks):
            data = stream.read(self.chunk_size)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        return self._frames_to_wav(frames)
    
    async def record_async(self, duration: float = 5.0) -> bytes:
        """Record audio asynchronously.
        
        Args:
            duration: Recording duration in seconds.
            
        Returns:
            Audio bytes in WAV format.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.record, duration)
    
    def _frames_to_wav(self, frames: list[bytes]) -> bytes:
        """Convert frames to WAV bytes."""
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
        
        buffer.seek(0)
        return buffer.read()
    
    def _create_mock_audio(self, duration: float) -> bytes:
        """Create mock audio data for testing."""
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            # Write silence
            num_samples = int(self.sample_rate * duration)
            wf.writeframes(b'\x00\x00' * num_samples)
        
        buffer.seek(0)
        return buffer.read()
    
    def close(self):
        """Close audio recorder."""
        if self._pyaudio:
            self._pyaudio.terminate()


class AudioPlayer:
    """Plays audio through speakers.
    
    Uses pygame for audio playback.
    """
    
    def __init__(self):
        """Initialize audio player."""
        self._initialized = False
        try:
            import pygame
            pygame.mixer.init()
            self._initialized = True
        except Exception:
            pass
    
    def play(self, audio_data: bytes, format: str = "mp3"):
        """Play audio data.
        
        Args:
            audio_data: Audio bytes to play.
            format: Audio format (mp3, wav).
        """
        if not self._initialized:
            return
        
        import pygame
        import io
        
        audio_buffer = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_buffer, format)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
    async def play_async(self, audio_data: bytes, format: str = "mp3"):
        """Play audio asynchronously.
        
        Args:
            audio_data: Audio bytes to play.
            format: Audio format.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.play, audio_data, format)
    
    def stop(self):
        """Stop playback."""
        if self._initialized:
            import pygame
            pygame.mixer.music.stop()

