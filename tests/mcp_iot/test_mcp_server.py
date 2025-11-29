"""Tests for MCP IoT Server - TDD: Write tests first."""

import pytest
from unittest.mock import MagicMock, AsyncMock


class TestMCPServer:
    """Tests for MCP IoT Server."""

    def test_mcp_server_has_tools(self):
        """MCP server should expose IoT control tools."""
        from home_ai.mcp_iot.server import create_mcp_server
        
        server = create_mcp_server()
        
        # Server should have tools registered
        assert hasattr(server, '_tool_manager') or hasattr(server, 'list_tools')
    
    def test_mcp_server_has_light_tool(self):
        """MCP server should have light control tool."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        tools = controller.get_tools()
        
        tool_names = [t["name"] for t in tools]
        assert "control_light" in tool_names
    
    def test_mcp_server_has_alarm_tool(self):
        """MCP server should have alarm control tool."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        tools = controller.get_tools()
        
        tool_names = [t["name"] for t in tools]
        assert "control_alarm" in tool_names
    
    def test_mcp_server_has_thermostat_tool(self):
        """MCP server should have thermostat control tool."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        tools = controller.get_tools()
        
        tool_names = [t["name"] for t in tools]
        assert "control_thermostat" in tool_names
    
    @pytest.mark.asyncio
    async def test_control_light_on(self):
        """Control light tool should turn light on."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        result = await controller.control_light(room="living_room", action="on")
        
        assert result["success"] is True
        assert "켰습니다" in result["message"]
    
    @pytest.mark.asyncio
    async def test_control_light_brightness(self):
        """Control light tool should set brightness."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        result = await controller.control_light(
            room="living_room",
            action="set_brightness",
            brightness=50
        )
        
        assert result["success"] is True
        assert "50%" in result["message"]
    
    @pytest.mark.asyncio
    async def test_control_alarm_set(self):
        """Control alarm tool should set alarm."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        result = await controller.control_alarm(action="set", time="07:00")
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_control_thermostat_temp(self):
        """Control thermostat tool should set temperature."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        result = await controller.control_thermostat(action="set_temp", temperature=24)
        
        assert result["success"] is True
        assert "24" in result["message"]
    
    def test_get_device_states(self):
        """IoT controller should return all device states."""
        from home_ai.mcp_iot.server import IoTController
        
        controller = IoTController()
        states = controller.get_all_states()
        
        assert "lights" in states
        assert "alarm" in states
        assert "thermostat" in states

