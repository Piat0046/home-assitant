"""REST API endpoints."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from home_ai.mcp_iot.server import IoTController

router = APIRouter(prefix="/api", tags=["api"])

# Global IoT controller instance
_iot_controller: IoTController | None = None


def get_iot_controller() -> IoTController:
    """Get IoT controller instance."""
    global _iot_controller
    if _iot_controller is None:
        _iot_controller = IoTController()
    return _iot_controller


class ChatRequestAPI(BaseModel):
    """API request model for chat endpoint."""

    text: str | None = Field(None, description="Text input")
    audio: str | None = Field(None, description="Base64 encoded audio")
    mode: str = Field("text", description="Input mode: text or audio")


class ChatResponseAPI(BaseModel):
    """API response model for chat endpoint."""

    text: str
    audio: str | None = None
    commands_executed: list[dict] = Field(default_factory=list)
    request_id: str


@router.post("/chat", response_model=ChatResponseAPI)
async def chat(request: ChatRequestAPI):
    """Process a chat request.

    Accepts text or audio input and returns AI response with IoT command results.
    """
    from home_ai.server.app import get_llm, get_stt, get_tts

    request_id = str(uuid4())

    # Validate input
    if request.mode == "text" and not request.text:
        raise HTTPException(status_code=400, detail="Text input required for text mode")
    if request.mode == "audio" and not request.audio:
        raise HTTPException(status_code=400, detail="Audio input required for audio mode")

    # Process input
    input_text = request.text

    if request.mode == "audio" and request.audio:
        import base64

        stt = get_stt()
        audio_bytes = base64.b64decode(request.audio)
        input_text = await stt.transcribe_async(audio_bytes)

    # Get LLM response
    llm = get_llm()
    response = await llm.process_async(input_text)

    # Prepare response
    result = ChatResponseAPI(
        text=response.text, commands_executed=[cmd.model_dump() for cmd in response.commands], request_id=request_id
    )

    # Generate audio response if needed
    if request.mode == "audio":
        import base64

        tts = get_tts()
        audio_bytes = await tts.synthesize_async(response.text)
        result.audio = base64.b64encode(audio_bytes).decode()

    return result


@router.get("/devices")
async def get_devices(controller: IoTController = Depends(get_iot_controller)):
    """Get current state of all IoT devices."""
    return controller.get_all_states()


class LightControlRequest(BaseModel):
    """Request model for light control."""

    room: str
    action: str
    brightness: int | None = None


@router.post("/devices/light")
async def control_light(request: LightControlRequest, controller: IoTController = Depends(get_iot_controller)):
    """Control a light device directly."""
    result = await controller.control_light(room=request.room, action=request.action, brightness=request.brightness)
    return result


class AlarmControlRequest(BaseModel):
    """Request model for alarm control."""

    action: str
    time: str | None = None
    label: str | None = None


@router.post("/devices/alarm")
async def control_alarm(request: AlarmControlRequest, controller: IoTController = Depends(get_iot_controller)):
    """Control the alarm device directly."""
    result = await controller.control_alarm(action=request.action, time=request.time, label=request.label)
    return result


class ThermostatControlRequest(BaseModel):
    """Request model for thermostat control."""

    action: str
    temperature: float | None = None
    mode: str | None = None


@router.post("/devices/thermostat")
async def control_thermostat(
    request: ThermostatControlRequest, controller: IoTController = Depends(get_iot_controller)
):
    """Control the thermostat device directly."""
    result = await controller.control_thermostat(
        action=request.action, temperature=request.temperature, mode=request.mode
    )
    return result
