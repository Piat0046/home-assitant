"""WebSocket API handler."""

from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        """Send JSON data to a client."""
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        """Broadcast data to all connected clients."""
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


def get_llm():
    """Get LLM instance. Import here to avoid circular imports."""
    from home_ai.server.app import get_llm as _get_llm

    return _get_llm()


def get_stt():
    """Get STT instance."""
    from home_ai.server.app import get_stt as _get_stt

    return _get_stt()


def get_tts():
    """Get TTS instance."""
    from home_ai.server.app import get_tts as _get_tts

    return _get_tts()


async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connection.

    Message format:
    {
        "type": "text" | "audio",
        "content": "message text" | "base64 audio",
        "request_id": "optional uuid"
    }

    Response format:
    {
        "type": "response",
        "text": "response text",
        "audio": "base64 audio (optional)",
        "commands": [...],
        "request_id": "uuid"
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            message_type = data.get("type", "text")
            content = data.get("content", "")
            request_id = data.get("request_id", str(uuid4()))

            try:
                # Process input
                input_text = content

                if message_type == "audio":
                    import base64

                    stt = get_stt()
                    audio_bytes = base64.b64decode(content)
                    input_text = await stt.transcribe_async(audio_bytes)

                # Get LLM response
                llm = get_llm()
                response = await llm.process_async(input_text)

                # Prepare response
                response_data = {
                    "type": "response",
                    "text": response.text,
                    "commands": [cmd.model_dump() for cmd in response.commands],
                    "request_id": request_id,
                }

                # Generate audio response if original was audio
                if message_type == "audio":
                    import base64

                    tts = get_tts()
                    audio_bytes = await tts.synthesize_async(response.text)
                    response_data["audio"] = base64.b64encode(audio_bytes).decode()

                await manager.send_json(websocket, response_data)

            except Exception as e:
                # Send error response
                await manager.send_json(websocket, {"type": "error", "message": str(e), "request_id": request_id})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
