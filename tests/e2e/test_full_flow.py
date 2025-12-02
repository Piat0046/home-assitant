"""End-to-end tests for the full assistant flow."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.e2e
class TestFullFlow:
    """End-to-end tests for the complete assistant flow."""

    @pytest.mark.asyncio
    async def test_text_to_iot_flow(self):
        """Test complete text input to IoT control flow."""
        from home_ai.common.models import IoTCommand, LLMResponse
        from home_ai.mcp_iot.server import IoTController

        # Create IoT controller
        controller = IoTController()

        # Simulate LLM response with IoT command
        llm_response = LLMResponse(
            text="거실 조명을 켰습니다.",
            commands=[IoTCommand(device="light", action="on", parameters={"room": "living_room"})],
        )

        # Execute commands
        for cmd in llm_response.commands:
            if cmd.device == "light":
                result = await controller.control_light(
                    room=cmd.parameters.get("room", "living_room"), action=cmd.action
                )
                assert result["success"] is True

        # Verify state changed
        states = controller.get_all_states()
        assert states["lights"]["living_room"]["power"] == "on"

    @pytest.mark.asyncio
    async def test_alarm_flow(self):
        """Test alarm setting flow."""
        from home_ai.mcp_iot.server import IoTController

        controller = IoTController()

        # Set alarm
        result = await controller.control_alarm(action="set", time="07:00", label="Wake up")
        assert result["success"] is True

        # Verify alarm is set
        states = controller.get_all_states()
        assert len(states["alarm"]["alarms"]) == 1

        # Cancel alarm
        result = await controller.control_alarm(action="cancel", time="07:00")
        assert result["success"] is True

        # Verify alarm is cancelled
        states = controller.get_all_states()
        assert len(states["alarm"]["alarms"]) == 0

    @pytest.mark.asyncio
    async def test_thermostat_flow(self):
        """Test thermostat control flow."""
        from home_ai.mcp_iot.server import IoTController

        controller = IoTController()

        # Set temperature
        result = await controller.control_thermostat(action="set_temp", temperature=24)
        assert result["success"] is True

        # Set mode
        result = await controller.control_thermostat(action="set_mode", mode="cooling")
        assert result["success"] is True

        # Verify state
        states = controller.get_all_states()
        assert states["thermostat"]["target_temp"] == 24
        assert states["thermostat"]["mode"] == "cooling"

    def test_server_api_health(self):
        """Test server health endpoint."""
        from fastapi.testclient import TestClient

        from home_ai.server.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_server_api_devices(self):
        """Test device status endpoint."""
        from fastapi.testclient import TestClient

        from home_ai.server.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/api/devices")
        assert response.status_code == 200

        data = response.json()
        assert "lights" in data
        assert "alarm" in data
        assert "thermostat" in data

    @pytest.mark.asyncio
    async def test_client_assistant_text_mode(self):
        """Test client assistant in text mode."""
        from home_ai.client.api_client import RESTClient
        from home_ai.client.assistant import ClientAssistant

        assistant = ClientAssistant(server_url="http://localhost:8000")

        # Mock API client
        mock_client = MagicMock(spec=RESTClient)
        mock_client.chat_async = AsyncMock(
            return_value={
                "text": "거실 조명을 켰습니다.",
                "commands_executed": [{"device": "light", "action": "on", "parameters": {"room": "living_room"}}],
                "request_id": "test-123",
            }
        )
        assistant._api_client = mock_client

        result = await assistant.process_text("거실 불 켜줘")

        assert "조명" in result["text"]
        assert len(result["commands_executed"]) == 1
