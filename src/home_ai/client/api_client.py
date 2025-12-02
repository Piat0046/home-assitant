"""API clients for communicating with the server."""

import base64
import json
from typing import Any

import httpx
import websocket


class RESTClient:
    """REST API client for the Home AI server.

    Provides synchronous and asynchronous methods for API communication.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize REST client.

        Args:
            base_url: Base URL of the server.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url)
        self._sync_client = httpx.Client(base_url=self.base_url)

    async def chat_async(
        self, text: str | None = None, audio: bytes | None = None, mode: str = "text"
    ) -> dict[str, Any]:
        """Send a chat request asynchronously.

        Args:
            text: Text input (for text mode).
            audio: Audio bytes (for audio mode).
            mode: Input mode ('text' or 'audio').

        Returns:
            Response dictionary with text and optional audio.
        """
        payload = {"mode": mode}

        if text:
            payload["text"] = text
        if audio:
            payload["audio"] = base64.b64encode(audio).decode()

        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()

        return response.json()

    def chat(self, text: str | None = None, audio: bytes | None = None, mode: str = "text") -> dict[str, Any]:
        """Send a chat request synchronously.

        Args:
            text: Text input (for text mode).
            audio: Audio bytes (for audio mode).
            mode: Input mode ('text' or 'audio').

        Returns:
            Response dictionary with text and optional audio.
        """
        payload = {"mode": mode}

        if text:
            payload["text"] = text
        if audio:
            payload["audio"] = base64.b64encode(audio).decode()

        response = self._sync_client.post("/api/chat", json=payload)
        response.raise_for_status()

        return response.json()

    async def get_devices_async(self) -> dict[str, Any]:
        """Get device states asynchronously."""
        response = await self._client.get("/api/devices")
        response.raise_for_status()
        return response.json()

    def get_devices(self) -> dict[str, Any]:
        """Get device states synchronously."""
        response = self._sync_client.get("/api/devices")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client connections."""
        await self._client.aclose()
        self._sync_client.close()


class WebSocketClient:
    """WebSocket client for real-time communication with the server.

    Provides methods for maintaining persistent connection and message exchange.
    """

    def __init__(self, url: str = "ws://localhost:8000/ws"):
        """Initialize WebSocket client.

        Args:
            url: WebSocket URL of the server.
        """
        self.url = url
        self._ws: websocket.WebSocket | None = None
        self._callbacks: dict[str, list] = {
            "response": [],
            "error": [],
        }

    def connect(self):
        """Connect to the WebSocket server."""
        self._ws = websocket.create_connection(self.url)

    def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self._ws:
            self._ws.close()
            self._ws = None

    def send_text(self, text: str, request_id: str | None = None) -> dict[str, Any]:
        """Send a text message and wait for response.

        Args:
            text: Text message to send.
            request_id: Optional request ID.

        Returns:
            Response dictionary.
        """
        if not self._ws:
            self.connect()

        message = {"type": "text", "content": text}
        if request_id:
            message["request_id"] = request_id

        self._ws.send(json.dumps(message))
        response = self._ws.recv()

        return json.loads(response)

    def send_audio(self, audio: bytes, request_id: str | None = None) -> dict[str, Any]:
        """Send an audio message and wait for response.

        Args:
            audio: Audio bytes to send.
            request_id: Optional request ID.

        Returns:
            Response dictionary.
        """
        if not self._ws:
            self.connect()

        message = {"type": "audio", "content": base64.b64encode(audio).decode()}
        if request_id:
            message["request_id"] = request_id

        self._ws.send(json.dumps(message))
        response = self._ws.recv()

        result = json.loads(response)

        # Decode audio response if present
        if result.get("audio"):
            result["audio_bytes"] = base64.b64decode(result["audio"])

        return result

    def on_response(self, callback):
        """Register a callback for response messages."""
        self._callbacks["response"].append(callback)

    def on_error(self, callback):
        """Register a callback for error messages."""
        self._callbacks["error"].append(callback)
