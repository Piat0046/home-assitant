"""Google Speech Recognition STT implementation."""

import asyncio

import speech_recognition as sr


class GoogleSTT:
    """Speech-to-Text using Google Speech Recognition.

    Uses the free Google Speech Recognition API via the SpeechRecognition library.
    Requires internet connection.
    """

    def __init__(self, language: str = "ko-KR"):
        """Initialize Google STT.

        Args:
            language: Language code for recognition (default: Korean).
        """
        self.language = language
        self._recognizer = sr.Recognizer()

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes (WAV format expected).

        Returns:
            Transcribed text string.

        Raises:
            sr.UnknownValueError: If speech is unintelligible.
            sr.RequestError: If API request fails.
        """
        # Convert bytes to AudioData
        audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)

        try:
            text = self._recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"API request failed: {e}")

    async def transcribe_async(self, audio_data: bytes) -> str:
        """Asynchronously transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes.

        Returns:
            Transcribed text string.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcribe, audio_data)
