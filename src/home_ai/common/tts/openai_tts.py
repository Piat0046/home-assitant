"""OpenAI TTS API implementation."""

import io
from typing import Literal

from openai import AsyncOpenAI, OpenAI

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class OpenAITTS:
    """Text-to-Speech using OpenAI TTS API.

    Uses OpenAI's TTS models for high-quality voice synthesis.
    Requires OpenAI API key.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "tts-1",
        voice: VoiceType = "alloy",
    ):
        """Initialize OpenAI TTS.

        Args:
            api_key: OpenAI API key.
            model: TTS model to use (tts-1 or tts-1-hd).
            voice: Voice to use for synthesis.
        """
        self.model = model
        self.voice = voice
        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)

    def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes in MP3 format.
        """
        response = self._client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
        )

        return response.content

    async def synthesize_async(self, text: str) -> bytes:
        """Asynchronously synthesize text to audio bytes.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes in MP3 format.
        """
        response = await self._async_client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
        )

        return response.content

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
