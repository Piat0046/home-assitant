"""Tests for IoT devices - TDD: Write tests first."""

from home_ai.common.models import IoTCommand


class TestLightDevice:
    """Tests for Light device."""

    def test_light_has_device_type(self):
        """Light should have device_type property."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        assert light.device_type == "light"

    def test_light_initial_state_is_off(self):
        """Light should be off by default."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        state = light.get_state()

        assert state["power"] == "off"
        assert state["brightness"] == 0

    def test_light_turn_on(self):
        """Light should turn on with 'on' action."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        cmd = IoTCommand(device="light", action="on", parameters={"room": "living_room"})

        result = light.execute(cmd)

        assert result.success is True
        assert light.get_state()["power"] == "on"
        assert light.get_state()["brightness"] == 100

    def test_light_turn_off(self):
        """Light should turn off with 'off' action."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        # Turn on first
        light.execute(IoTCommand(device="light", action="on"))
        # Then turn off
        result = light.execute(IoTCommand(device="light", action="off"))

        assert result.success is True
        assert light.get_state()["power"] == "off"

    def test_light_set_brightness(self):
        """Light should set brightness with 'set_brightness' action."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        cmd = IoTCommand(device="light", action="set_brightness", parameters={"brightness": 50})

        result = light.execute(cmd)

        assert result.success is True
        assert light.get_state()["brightness"] == 50
        assert light.get_state()["power"] == "on"

    def test_light_invalid_action(self):
        """Light should handle invalid actions gracefully."""
        from home_ai.mcp_iot.devices.light import Light

        light = Light(room="living_room")
        cmd = IoTCommand(device="light", action="invalid_action")

        result = light.execute(cmd)

        assert result.success is False


class TestAlarmDevice:
    """Tests for Alarm device."""

    def test_alarm_has_device_type(self):
        """Alarm should have device_type property."""
        from home_ai.mcp_iot.devices.alarm import Alarm

        alarm = Alarm()
        assert alarm.device_type == "alarm"

    def test_alarm_initial_state(self):
        """Alarm should have no alarms set by default."""
        from home_ai.mcp_iot.devices.alarm import Alarm

        alarm = Alarm()
        state = alarm.get_state()

        assert state["alarms"] == []

    def test_alarm_set(self):
        """Alarm should set alarm with 'set' action."""
        from home_ai.mcp_iot.devices.alarm import Alarm

        alarm = Alarm()
        cmd = IoTCommand(device="alarm", action="set", parameters={"time": "07:00", "label": "Wake up"})

        result = alarm.execute(cmd)

        assert result.success is True
        state = alarm.get_state()
        assert len(state["alarms"]) == 1
        assert state["alarms"][0]["time"] == "07:00"

    def test_alarm_cancel(self):
        """Alarm should cancel alarm with 'cancel' action."""
        from home_ai.mcp_iot.devices.alarm import Alarm

        alarm = Alarm()
        # Set an alarm first
        alarm.execute(IoTCommand(device="alarm", action="set", parameters={"time": "07:00", "label": "Wake up"}))

        # Cancel it
        result = alarm.execute(IoTCommand(device="alarm", action="cancel", parameters={"time": "07:00"}))

        assert result.success is True
        assert len(alarm.get_state()["alarms"]) == 0

    def test_alarm_list(self):
        """Alarm should list all alarms with 'list' action."""
        from home_ai.mcp_iot.devices.alarm import Alarm

        alarm = Alarm()
        alarm.execute(IoTCommand(device="alarm", action="set", parameters={"time": "07:00"}))
        alarm.execute(IoTCommand(device="alarm", action="set", parameters={"time": "08:00"}))

        result = alarm.execute(IoTCommand(device="alarm", action="list"))

        assert result.success is True
        assert len(result.data["alarms"]) == 2


class TestThermostatDevice:
    """Tests for Thermostat device."""

    def test_thermostat_has_device_type(self):
        """Thermostat should have device_type property."""
        from home_ai.mcp_iot.devices.thermostat import Thermostat

        thermostat = Thermostat()
        assert thermostat.device_type == "thermostat"

    def test_thermostat_initial_state(self):
        """Thermostat should have default temperature."""
        from home_ai.mcp_iot.devices.thermostat import Thermostat

        thermostat = Thermostat()
        state = thermostat.get_state()

        assert "current_temp" in state
        assert "target_temp" in state
        assert "mode" in state

    def test_thermostat_set_temperature(self):
        """Thermostat should set target temperature with 'set_temp' action."""
        from home_ai.mcp_iot.devices.thermostat import Thermostat

        thermostat = Thermostat()
        cmd = IoTCommand(device="thermostat", action="set_temp", parameters={"temperature": 24})

        result = thermostat.execute(cmd)

        assert result.success is True
        assert thermostat.get_state()["target_temp"] == 24

    def test_thermostat_set_mode(self):
        """Thermostat should set mode with 'set_mode' action."""
        from home_ai.mcp_iot.devices.thermostat import Thermostat

        thermostat = Thermostat()
        cmd = IoTCommand(device="thermostat", action="set_mode", parameters={"mode": "cooling"})

        result = thermostat.execute(cmd)

        assert result.success is True
        assert thermostat.get_state()["mode"] == "cooling"

    def test_thermostat_turn_off(self):
        """Thermostat should turn off with 'off' action."""
        from home_ai.mcp_iot.devices.thermostat import Thermostat

        thermostat = Thermostat()
        result = thermostat.execute(IoTCommand(device="thermostat", action="off"))

        assert result.success is True
        assert thermostat.get_state()["mode"] == "off"
