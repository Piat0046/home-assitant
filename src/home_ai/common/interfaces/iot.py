"""IoT Device interface protocol."""

from typing import Any, Protocol, runtime_checkable

from home_ai.common.models import IoTCommand, IoTResult


@runtime_checkable
class IoTDeviceInterface(Protocol):
    """Protocol for IoT device implementations.
    
    All IoT device implementations should conform to this interface.
    Devices can execute commands and report their current state.
    """
    
    @property
    def device_type(self) -> str:
        """Get the device type identifier.
        
        Returns:
            Device type string (e.g., 'light', 'alarm', 'thermostat').
        """
        ...
    
    def execute(self, command: IoTCommand) -> IoTResult:
        """Execute a command on the device.
        
        Args:
            command: The IoT command to execute.
            
        Returns:
            Result of the command execution.
        """
        ...
    
    def get_state(self) -> dict[str, Any]:
        """Get the current state of the device.
        
        Returns:
            Dictionary containing current device state.
        """
        ...

