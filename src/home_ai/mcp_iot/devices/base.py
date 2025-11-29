"""Base class for IoT devices."""

from abc import ABC, abstractmethod
from typing import Any

from home_ai.common.models import IoTCommand, IoTResult


class BaseDevice(ABC):
    """Abstract base class for IoT devices."""
    
    @property
    @abstractmethod
    def device_type(self) -> str:
        """Get the device type identifier."""
        ...
    
    @abstractmethod
    def execute(self, command: IoTCommand) -> IoTResult:
        """Execute a command on the device."""
        ...
    
    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """Get the current state of the device."""
        ...

