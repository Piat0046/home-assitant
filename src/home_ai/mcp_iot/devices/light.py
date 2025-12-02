"""Light device implementation."""

from typing import Any

from home_ai.common.models import IoTCommand, IoTResult
from home_ai.mcp_iot.devices.base import BaseDevice


class Light(BaseDevice):
    """Simulated light device.

    Supports on/off control and brightness adjustment.
    """

    def __init__(self, room: str = "default"):
        """Initialize light device.

        Args:
            room: Room identifier where the light is located.
        """
        self.room = room
        self._power = "off"
        self._brightness = 0

    @property
    def device_type(self) -> str:
        """Get device type."""
        return "light"

    def execute(self, command: IoTCommand) -> IoTResult:
        """Execute a command on the light.

        Supported actions:
        - on: Turn light on (100% brightness)
        - off: Turn light off
        - set_brightness: Set brightness level (0-100)
        """
        action = command.action
        params = command.parameters

        if action == "on":
            self._power = "on"
            self._brightness = 100
            return IoTResult(success=True, message=f"{self.room} 조명을 켰습니다.", data=self.get_state())

        elif action == "off":
            self._power = "off"
            self._brightness = 0
            return IoTResult(success=True, message=f"{self.room} 조명을 껐습니다.", data=self.get_state())

        elif action == "set_brightness":
            brightness = params.get("brightness", 100)
            brightness = max(0, min(100, brightness))  # Clamp to 0-100
            self._brightness = brightness
            self._power = "on" if brightness > 0 else "off"
            return IoTResult(
                success=True, message=f"{self.room} 조명 밝기를 {brightness}%로 설정했습니다.", data=self.get_state()
            )

        else:
            return IoTResult(success=False, message=f"알 수 없는 동작: {action}", data={})

    def get_state(self) -> dict[str, Any]:
        """Get current light state."""
        return {
            "room": self.room,
            "power": self._power,
            "brightness": self._brightness,
        }
