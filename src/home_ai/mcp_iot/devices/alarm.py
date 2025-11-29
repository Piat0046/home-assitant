"""Alarm device implementation."""

from typing import Any
from datetime import datetime

from home_ai.common.models import IoTCommand, IoTResult
from home_ai.mcp_iot.devices.base import BaseDevice


class Alarm(BaseDevice):
    """Simulated alarm device.
    
    Supports setting, canceling, and listing alarms.
    """
    
    def __init__(self):
        """Initialize alarm device."""
        self._alarms: list[dict[str, Any]] = []
    
    @property
    def device_type(self) -> str:
        """Get device type."""
        return "alarm"
    
    def execute(self, command: IoTCommand) -> IoTResult:
        """Execute a command on the alarm.
        
        Supported actions:
        - set: Set a new alarm (requires 'time' parameter)
        - cancel: Cancel an alarm (requires 'time' parameter)
        - list: List all alarms
        """
        action = command.action
        params = command.parameters
        
        if action == "set":
            time = params.get("time")
            label = params.get("label", "")
            
            if not time:
                return IoTResult(
                    success=False,
                    message="알람 시간을 지정해주세요.",
                    data={}
                )
            
            alarm = {
                "time": time,
                "label": label,
                "enabled": True,
                "created_at": datetime.now().isoformat()
            }
            self._alarms.append(alarm)
            
            return IoTResult(
                success=True,
                message=f"{time}에 알람을 설정했습니다.",
                data={"alarm": alarm}
            )
        
        elif action == "cancel":
            time = params.get("time")
            
            if not time:
                return IoTResult(
                    success=False,
                    message="취소할 알람 시간을 지정해주세요.",
                    data={}
                )
            
            original_count = len(self._alarms)
            self._alarms = [a for a in self._alarms if a["time"] != time]
            
            if len(self._alarms) < original_count:
                return IoTResult(
                    success=True,
                    message=f"{time} 알람을 취소했습니다.",
                    data=self.get_state()
                )
            else:
                return IoTResult(
                    success=False,
                    message=f"{time}에 설정된 알람이 없습니다.",
                    data={}
                )
        
        elif action == "list":
            return IoTResult(
                success=True,
                message=f"{len(self._alarms)}개의 알람이 설정되어 있습니다.",
                data={"alarms": self._alarms}
            )
        
        else:
            return IoTResult(
                success=False,
                message=f"알 수 없는 동작: {action}",
                data={}
            )
    
    def get_state(self) -> dict[str, Any]:
        """Get current alarm state."""
        return {
            "alarms": self._alarms,
        }

