"""Thermostat device implementation."""

from typing import Any, Literal

from home_ai.common.models import IoTCommand, IoTResult
from home_ai.mcp_iot.devices.base import BaseDevice

ThermostatMode = Literal["off", "heating", "cooling", "auto"]


class Thermostat(BaseDevice):
    """Simulated thermostat device.

    Supports temperature and mode control.
    """

    def __init__(self, current_temp: float = 22.0, target_temp: float = 22.0):
        """Initialize thermostat device.

        Args:
            current_temp: Current room temperature.
            target_temp: Target temperature setting.
        """
        self._current_temp = current_temp
        self._target_temp = target_temp
        self._mode: ThermostatMode = "auto"

    @property
    def device_type(self) -> str:
        """Get device type."""
        return "thermostat"

    def execute(self, command: IoTCommand) -> IoTResult:
        """Execute a command on the thermostat.

        Supported actions:
        - set_temp: Set target temperature (requires 'temperature' parameter)
        - set_mode: Set mode ('off', 'heating', 'cooling', 'auto')
        - off: Turn off thermostat
        """
        action = command.action
        params = command.parameters

        if action == "set_temp":
            temp = params.get("temperature")

            if temp is None:
                return IoTResult(success=False, message="온도를 지정해주세요.", data={})

            # Clamp temperature to reasonable range
            temp = max(10, min(35, float(temp)))
            self._target_temp = temp

            # Auto-enable if was off
            if self._mode == "off":
                self._mode = "auto"

            return IoTResult(success=True, message=f"온도를 {temp}°C로 설정했습니다.", data=self.get_state())

        elif action == "set_mode":
            mode = params.get("mode")

            if mode not in ("off", "heating", "cooling", "auto"):
                return IoTResult(success=False, message=f"지원하지 않는 모드입니다: {mode}", data={})

            self._mode = mode

            mode_names = {"off": "끔", "heating": "난방", "cooling": "냉방", "auto": "자동"}

            return IoTResult(
                success=True, message=f"모드를 {mode_names[mode]}(으)로 설정했습니다.", data=self.get_state()
            )

        elif action == "off":
            self._mode = "off"
            return IoTResult(success=True, message="온도 조절기를 껐습니다.", data=self.get_state())

        else:
            return IoTResult(success=False, message=f"알 수 없는 동작: {action}", data={})

    def get_state(self) -> dict[str, Any]:
        """Get current thermostat state."""
        return {
            "current_temp": self._current_temp,
            "target_temp": self._target_temp,
            "mode": self._mode,
        }
