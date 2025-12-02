"""Text-to-Speech interface protocol."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TTSInterface(Protocol):
    """Protocol for Text-to-Speech implementations.

    All TTS implementations should conform to this interface.
    Supports both synthesis (returning audio bytes) and direct playback.
    """

    def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes (typically MP3 or WAV format).
        """
        ...

    async def synthesize_async(self, text: str) -> bytes:
        """Asynchronously synthesize text to audio bytes.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes (typically MP3 or WAV format).
        """
        ...

    def speak(self, text: str) -> None:
        """Synthesize and immediately play audio.

        Args:
            text: Text to speak.
        """
        ...
