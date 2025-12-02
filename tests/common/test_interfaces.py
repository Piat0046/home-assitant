"""Tests for Protocol interfaces - TDD: Write tests first."""


class TestSTTInterface:
    """Tests for STT (Speech-to-Text) interface."""

    def test_stt_interface_has_transcribe_method(self):
        """STT interface should have transcribe method."""
        from home_ai.common.interfaces import STTInterface

        assert hasattr(STTInterface, "transcribe")

    def test_stt_interface_has_transcribe_async_method(self):
        """STT interface should have async transcribe method."""
        from home_ai.common.interfaces import STTInterface

        assert hasattr(STTInterface, "transcribe_async")

    def test_stt_interface_is_runtime_checkable(self):
        """STT interface should be runtime checkable."""
        from home_ai.common.interfaces import STTInterface

        assert hasattr(STTInterface, "__protocol_attrs__") or isinstance(STTInterface, type)


class TestTTSInterface:
    """Tests for TTS (Text-to-Speech) interface."""

    def test_tts_interface_has_synthesize_method(self):
        """TTS interface should have synthesize method."""
        from home_ai.common.interfaces import TTSInterface

        assert hasattr(TTSInterface, "synthesize")

    def test_tts_interface_has_synthesize_async_method(self):
        """TTS interface should have async synthesize method."""
        from home_ai.common.interfaces import TTSInterface

        assert hasattr(TTSInterface, "synthesize_async")

    def test_tts_interface_has_speak_method(self):
        """TTS interface should have speak method for direct playback."""
        from home_ai.common.interfaces import TTSInterface

        assert hasattr(TTSInterface, "speak")


class TestLLMInterface:
    """Tests for LLM interface."""

    def test_llm_interface_has_process_method(self):
        """LLM interface should have process method."""
        from home_ai.common.interfaces import LLMInterface

        assert hasattr(LLMInterface, "process")

    def test_llm_interface_has_process_async_method(self):
        """LLM interface should have async process method."""
        from home_ai.common.interfaces import LLMInterface

        assert hasattr(LLMInterface, "process_async")


class TestIoTDeviceInterface:
    """Tests for IoT Device interface."""

    def test_iot_interface_has_execute_method(self):
        """IoT device interface should have execute method."""
        from home_ai.common.interfaces import IoTDeviceInterface

        assert hasattr(IoTDeviceInterface, "execute")

    def test_iot_interface_has_get_state_method(self):
        """IoT device interface should have get_state method."""
        from home_ai.common.interfaces import IoTDeviceInterface

        assert hasattr(IoTDeviceInterface, "get_state")

    def test_iot_interface_has_device_type_property(self):
        """IoT device interface should have device_type property."""
        from home_ai.common.interfaces import IoTDeviceInterface

        assert hasattr(IoTDeviceInterface, "device_type")
