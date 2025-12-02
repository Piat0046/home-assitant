"""Protocol interfaces for dependency injection."""

from home_ai.common.interfaces.iot import IoTDeviceInterface
from home_ai.common.interfaces.llm import LLMInterface
from home_ai.common.interfaces.stt import STTInterface
from home_ai.common.interfaces.tts import TTSInterface

__all__ = ["STTInterface", "TTSInterface", "LLMInterface", "IoTDeviceInterface"]
