"""MCP IoT Server implementation."""

import asyncio
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from home_ai.common.models import IoTCommand
from home_ai.mcp_iot.devices.light import Light
from home_ai.mcp_iot.devices.alarm import Alarm
from home_ai.mcp_iot.devices.thermostat import Thermostat


class IoTController:
    """Controller for managing IoT devices.
    
    Provides a unified interface for controlling all IoT devices.
    """
    
    def __init__(self):
        """Initialize IoT controller with default devices."""
        self._lights: dict[str, Light] = {
            "living_room": Light(room="거실"),
            "bedroom": Light(room="침실"),
            "kitchen": Light(room="주방"),
        }
        self._alarm = Alarm()
        self._thermostat = Thermostat()
    
    def get_tools(self) -> list[dict[str, Any]]:
        """Get list of available tools for MCP."""
        return [
            {
                "name": "control_light",
                "description": "조명을 제어합니다. 켜기, 끄기, 밝기 조절이 가능합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "room": {
                            "type": "string",
                            "description": "방 이름 (living_room, bedroom, kitchen)",
                            "enum": ["living_room", "bedroom", "kitchen"]
                        },
                        "action": {
                            "type": "string",
                            "description": "동작 (on, off, set_brightness)",
                            "enum": ["on", "off", "set_brightness"]
                        },
                        "brightness": {
                            "type": "integer",
                            "description": "밝기 (0-100), set_brightness 동작 시 필요",
                            "minimum": 0,
                            "maximum": 100
                        }
                    },
                    "required": ["room", "action"]
                }
            },
            {
                "name": "control_alarm",
                "description": "알람을 제어합니다. 설정, 취소, 목록 조회가 가능합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "동작 (set, cancel, list)",
                            "enum": ["set", "cancel", "list"]
                        },
                        "time": {
                            "type": "string",
                            "description": "알람 시간 (HH:MM 형식)",
                            "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                        },
                        "label": {
                            "type": "string",
                            "description": "알람 라벨"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "control_thermostat",
                "description": "온도 조절기를 제어합니다. 온도 설정, 모드 변경이 가능합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "동작 (set_temp, set_mode, off)",
                            "enum": ["set_temp", "set_mode", "off"]
                        },
                        "temperature": {
                            "type": "number",
                            "description": "목표 온도 (10-35°C)",
                            "minimum": 10,
                            "maximum": 35
                        },
                        "mode": {
                            "type": "string",
                            "description": "모드 (heating, cooling, auto)",
                            "enum": ["heating", "cooling", "auto"]
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "get_device_status",
                "description": "모든 디바이스의 현재 상태를 조회합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def control_light(
        self,
        room: str,
        action: str,
        brightness: Optional[int] = None
    ) -> dict[str, Any]:
        """Control a light device.
        
        Args:
            room: Room identifier.
            action: Action to perform (on, off, set_brightness).
            brightness: Brightness level for set_brightness action.
            
        Returns:
            Result dictionary with success status and message.
        """
        if room not in self._lights:
            return {"success": False, "message": f"알 수 없는 방: {room}"}
        
        light = self._lights[room]
        params = {}
        if brightness is not None:
            params["brightness"] = brightness
        
        command = IoTCommand(device="light", action=action, parameters=params)
        result = light.execute(command)
        
        return {
            "success": result.success,
            "message": result.message,
            "state": result.data
        }
    
    async def control_alarm(
        self,
        action: str,
        time: Optional[str] = None,
        label: Optional[str] = None
    ) -> dict[str, Any]:
        """Control the alarm device.
        
        Args:
            action: Action to perform (set, cancel, list).
            time: Alarm time in HH:MM format.
            label: Optional alarm label.
            
        Returns:
            Result dictionary with success status and message.
        """
        params = {}
        if time:
            params["time"] = time
        if label:
            params["label"] = label
        
        command = IoTCommand(device="alarm", action=action, parameters=params)
        result = self._alarm.execute(command)
        
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data
        }
    
    async def control_thermostat(
        self,
        action: str,
        temperature: Optional[float] = None,
        mode: Optional[str] = None
    ) -> dict[str, Any]:
        """Control the thermostat device.
        
        Args:
            action: Action to perform (set_temp, set_mode, off).
            temperature: Target temperature.
            mode: Thermostat mode.
            
        Returns:
            Result dictionary with success status and message.
        """
        params = {}
        if temperature is not None:
            params["temperature"] = temperature
        if mode:
            params["mode"] = mode
        
        command = IoTCommand(device="thermostat", action=action, parameters=params)
        result = self._thermostat.execute(command)
        
        return {
            "success": result.success,
            "message": result.message,
            "state": result.data
        }
    
    def get_all_states(self) -> dict[str, Any]:
        """Get current state of all devices.
        
        Returns:
            Dictionary containing all device states.
        """
        return {
            "lights": {room: light.get_state() for room, light in self._lights.items()},
            "alarm": self._alarm.get_state(),
            "thermostat": self._thermostat.get_state(),
        }


def create_mcp_server() -> Server:
    """Create and configure the MCP server.
    
    Returns:
        Configured MCP Server instance.
    """
    server = Server("home-ai-iot")
    controller = IoTController()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        tools = controller.get_tools()
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"]
            )
            for t in tools
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        if name == "control_light":
            result = await controller.control_light(**arguments)
        elif name == "control_alarm":
            result = await controller.control_alarm(**arguments)
        elif name == "control_thermostat":
            result = await controller.control_thermostat(**arguments)
        elif name == "get_device_status":
            result = {
                "success": True,
                "message": "디바이스 상태 조회 완료",
                "states": controller.get_all_states()
            }
        else:
            result = {"success": False, "message": f"Unknown tool: {name}"}
        
        import json
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    
    return server


async def main():
    """Run the MCP server."""
    server = create_mcp_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

