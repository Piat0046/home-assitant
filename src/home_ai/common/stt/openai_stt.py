"""OpenAI Whisper API STT implementation."""

import io

from openai import AsyncOpenAI, OpenAI


class OpenAISTT:
    """Speech-to-Text using OpenAI Whisper API.

    Uses the OpenAI Whisper model for high-quality transcription.
    Requires OpenAI API key.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "whisper-1",
        language: str = "ko",
    ):
        """Initialize OpenAI STT.

        Args:
            api_key: OpenAI API key.
            model: Whisper model to use.
            language: Language code for transcription.
        """
        self.model = model
        self.language = language
        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes.

        Returns:
            Transcribed text string.
        """
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        response = self._client.audio.transcriptions.create(
            model=self.model,
            file=audio_file,
            language=self.language,
        )

        return response.text

    async def transcribe_async(self, audio_data: bytes) -> str:
        """Asynchronously transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes.

        Returns:
            Transcribed text string.
        """
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        response = await self._async_client.audio.transcriptions.create(
            model=self.model,
            file=audio_file,
            language=self.language,
        )

        return response.text
