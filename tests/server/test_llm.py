"""Tests for LLM module - TDD: Write tests first."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestOpenAILLM:
    """Tests for OpenAI LLM implementation."""

    def test_openai_llm_implements_interface(self):
        """OpenAI LLM should implement LLMInterface."""
        from home_ai.server.llm.openai_llm import OpenAILLM

        llm = OpenAILLM(api_key="test_key")
        assert hasattr(llm, "process")
        assert hasattr(llm, "process_async")

    def test_openai_llm_has_tools(self):
        """OpenAI LLM should have IoT tools configured."""
        from home_ai.server.llm.openai_llm import OpenAILLM

        llm = OpenAILLM(api_key="test_key")
        assert len(llm._tools) > 0

    @pytest.mark.asyncio
    async def test_openai_llm_process_text_response(self):
        """OpenAI LLM should return text response."""
        from home_ai.common.models import LLMResponse
        from home_ai.server.llm.openai_llm import OpenAILLM

        llm = OpenAILLM(api_key="test_key")

        # Mock the client
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "네, 거실 조명을 켜겠습니다."
        mock_message.tool_calls = None
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]

        llm._async_client = MagicMock()
        llm._async_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await llm.process_async("거실 불 켜줘")

        assert isinstance(result, LLMResponse)
        assert result.text == "네, 거실 조명을 켜겠습니다."

    @pytest.mark.asyncio
    async def test_openai_llm_process_with_tool_call(self):
        """OpenAI LLM should handle tool calls."""
        from home_ai.common.models import LLMResponse
        from home_ai.server.llm.openai_llm import OpenAILLM

        llm = OpenAILLM(api_key="test_key")

        # Mock tool call response
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "control_light"
        mock_tool_call.function.arguments = json.dumps({"room": "living_room", "action": "on"})

        # First response with tool call
        mock_response1 = MagicMock()
        mock_choice1 = MagicMock()
        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]
        mock_choice1.message = mock_message1
        mock_choice1.finish_reason = "tool_calls"
        mock_response1.choices = [mock_choice1]

        # Second response after tool execution
        mock_response2 = MagicMock()
        mock_choice2 = MagicMock()
        mock_message2 = MagicMock()
        mock_message2.content = "거실 조명을 켰습니다."
        mock_message2.tool_calls = None
        mock_choice2.message = mock_message2
        mock_choice2.finish_reason = "stop"
        mock_response2.choices = [mock_choice2]

        llm._async_client = MagicMock()
        llm._async_client.chat.completions.create = AsyncMock(side_effect=[mock_response1, mock_response2])

        # Mock tool executor
        llm._tool_executor = AsyncMock(return_value={"success": True, "message": "거실 조명을 켰습니다."})

        result = await llm.process_async("거실 불 켜줘")

        assert isinstance(result, LLMResponse)
        assert len(result.commands) > 0


class TestClaudeLLM:
    """Tests for Claude LLM implementation."""

    def test_claude_llm_implements_interface(self):
        """Claude LLM should implement LLMInterface."""
        from home_ai.server.llm.claude_llm import ClaudeLLM

        llm = ClaudeLLM(api_key="test_key")
        assert hasattr(llm, "process")
        assert hasattr(llm, "process_async")

    def test_claude_llm_has_tools(self):
        """Claude LLM should have IoT tools configured."""
        from home_ai.server.llm.claude_llm import ClaudeLLM

        llm = ClaudeLLM(api_key="test_key")
        assert len(llm._tools) > 0

    @pytest.mark.asyncio
    async def test_claude_llm_process_text_response(self):
        """Claude LLM should return text response."""
        from home_ai.common.models import LLMResponse
        from home_ai.server.llm.claude_llm import ClaudeLLM

        llm = ClaudeLLM(api_key="test_key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="네, 거실 조명을 켜겠습니다.")]
        mock_response.stop_reason = "end_turn"

        llm._async_client = MagicMock()
        llm._async_client.messages.create = AsyncMock(return_value=mock_response)

        result = await llm.process_async("거실 불 켜줘")

        assert isinstance(result, LLMResponse)
        assert "조명" in result.text or "켜" in result.text
