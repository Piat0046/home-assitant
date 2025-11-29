"""Client-side assistant implementation."""

import asyncio
from typing import Any, Optional

from home_ai.client.api_client import RESTClient, WebSocketClient
from home_ai.client.audio import AudioRecorder, AudioPlayer
from home_ai.common.config import get_settings
from home_ai.logging.file_logger import get_client_logger


class ClientAssistant:
    """Client-side voice assistant.
    
    Handles audio I/O and communication with the server.
    Supports both text and audio modes.
    """
    
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        use_websocket: bool = False,
        use_local_stt: bool = False,
        use_local_tts: bool = False,
    ):
        """Initialize client assistant.
        
        Args:
            server_url: Server URL.
            use_websocket: Use WebSocket instead of REST.
            use_local_stt: Process STT locally instead of server.
            use_local_tts: Process TTS locally instead of server.
        """
        self.server_url = server_url
        self.use_websocket = use_websocket
        self.use_local_stt = use_local_stt
        self.use_local_tts = use_local_tts
        
        # API client
        if use_websocket:
            ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
            self._api_client = WebSocketClient(url=ws_url)
        else:
            self._api_client = RESTClient(base_url=server_url)
        
        # Audio I/O
        self._recorder = AudioRecorder()
        self._player = AudioPlayer()
        
        # Local STT/TTS (optional)
        self._stt = None
        self._tts = None
        
        if use_local_stt:
            settings = get_settings()
            if settings.stt_provider == "openai":
                from home_ai.common.stt.openai_stt import OpenAISTT
                self._stt = OpenAISTT(api_key=settings.openai_api_key)
            else:
                from home_ai.common.stt.google_stt import GoogleSTT
                self._stt = GoogleSTT()
        
        if use_local_tts:
            settings = get_settings()
            if settings.tts_provider == "openai":
                from home_ai.common.tts.openai_tts import OpenAITTS
                self._tts = OpenAITTS(api_key=settings.openai_api_key)
            else:
                from home_ai.common.tts.gtts_impl import GTTSImpl
                self._tts = GTTSImpl()
        
        # Logger
        self._logger = get_client_logger()
    
    async def process_text(self, text: str) -> dict[str, Any]:
        """Process text input.
        
        Args:
            text: User text input.
            
        Returns:
            Response dictionary.
        """
        self._logger.info(f"Processing text: {text}")
        
        if isinstance(self._api_client, RESTClient):
            result = await self._api_client.chat_async(text=text, mode="text")
        else:
            # WebSocket - need to implement async version
            result = self._api_client.send_text(text)
        
        self._logger.info(f"Response: {result.get('text', '')}")
        
        return result
    
    async def process_audio(self, audio_data: Optional[bytes] = None, duration: float = 5.0) -> dict[str, Any]:
        """Process audio input.
        
        Args:
            audio_data: Pre-recorded audio bytes. If None, records from mic.
            duration: Recording duration if recording from mic.
            
        Returns:
            Response dictionary.
        """
        # Record audio if not provided
        if audio_data is None:
            self._logger.info(f"Recording audio for {duration}s...")
            audio_data = await self._recorder.record_async(duration)
        
        # Local STT if enabled
        if self.use_local_stt and self._stt:
            self._logger.info("Transcribing locally...")
            text = await self._stt.transcribe_async(audio_data)
            result = await self.process_text(text)
        else:
            # Send audio to server
            self._logger.info("Sending audio to server...")
            if isinstance(self._api_client, RESTClient):
                result = await self._api_client.chat_async(audio=audio_data, mode="audio")
            else:
                result = self._api_client.send_audio(audio_data)
        
        # Play audio response
        if result.get("audio"):
            import base64
            audio_response = base64.b64decode(result["audio"])
            await self._player.play_async(audio_response)
        elif self.use_local_tts and self._tts:
            audio_response = await self._tts.synthesize_async(result["text"])
            await self._player.play_async(audio_response)
        
        return result
    
    async def run_interactive(self):
        """Run interactive voice assistant loop."""
        print("Home AI Assistant 시작됨. '종료'를 입력하면 종료됩니다.")
        print("텍스트 입력 또는 Enter를 눌러 음성 녹음을 시작합니다.")
        
        while True:
            try:
                user_input = input("\n> ")
                
                if user_input.lower() in ["종료", "exit", "quit"]:
                    print("종료합니다.")
                    break
                
                if user_input.strip():
                    # Text mode
                    result = await self.process_text(user_input)
                    print(f"\n🏠 {result.get('text', '')}")
                else:
                    # Audio mode
                    print("🎤 녹음 중... (5초)")
                    result = await self.process_audio(duration=5.0)
                    print(f"\n🏠 {result.get('text', '')}")
                
            except KeyboardInterrupt:
                print("\n종료합니다.")
                break
            except Exception as e:
                self._logger.error(f"Error: {e}")
                print(f"오류가 발생했습니다: {e}")
    
    async def close(self):
        """Close the assistant and cleanup resources."""
        if isinstance(self._api_client, RESTClient):
            await self._api_client.close()
        elif isinstance(self._api_client, WebSocketClient):
            self._api_client.disconnect()
        
        self._recorder.close()


async def main():
    """Main entry point for client."""
    settings = get_settings()
    
    assistant = ClientAssistant(
        server_url=f"http://{settings.server_host}:{settings.server_port}",
        use_websocket=False,
        use_local_stt=settings.stt_provider != "google",  # Use local if not Google
        use_local_tts=settings.tts_provider != "gtts",
    )
    
    try:
        await assistant.run_interactive()
    finally:
        await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())

