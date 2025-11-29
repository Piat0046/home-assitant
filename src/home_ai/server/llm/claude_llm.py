"""Claude LLM implementation."""

import asyncio
import json
from typing import Any, Optional

from anthropic import Anthropic, AsyncAnthropic

from home_ai.common.models import LLMResponse, IoTCommand
from home_ai.mcp_iot.server import IoTController


class ClaudeLLM:
    """LLM using Anthropic Claude models with tool use.
    
    Integrates with IoT controller for device control.
    """
    
    SYSTEM_PROMPT = """당신은 스마트 홈 AI 어시스턴트입니다.
사용자의 음성 명령을 이해하고 적절한 IoT 디바이스를 제어합니다.

사용 가능한 디바이스:
- 조명 (거실, 침실, 주방): 켜기, 끄기, 밝기 조절
- 알람: 설정, 취소, 목록 조회
- 온도 조절기: 온도 설정, 모드 변경

항상 친절하고 자연스러운 한국어로 응답해주세요."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        iot_controller: Optional[IoTController] = None,
    ):
        """Initialize Claude LLM.
        
        Args:
            api_key: Anthropic API key.
            model: Model to use.
            iot_controller: IoT controller for device control.
        """
        self.model = model
        self._client = Anthropic(api_key=api_key)
        self._async_client = AsyncAnthropic(api_key=api_key)
        self._iot_controller = iot_controller or IoTController()
        self._tools = self._create_tools()
    
    def _create_tools(self) -> list[dict[str, Any]]:
        """Create Claude tool definitions from IoT controller."""
        iot_tools = self._iot_controller.get_tools()
        
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["inputSchema"]
            }
            for tool in iot_tools
        ]
    
    async def _execute_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """Execute an IoT tool.
        
        Args:
            name: Tool name.
            arguments: Tool arguments.
            
        Returns:
            Tool execution result.
        """
        if name == "control_light":
            return await self._iot_controller.control_light(**arguments)
        elif name == "control_alarm":
            return await self._iot_controller.control_alarm(**arguments)
        elif name == "control_thermostat":
            return await self._iot_controller.control_thermostat(**arguments)
        elif name == "get_device_status":
            return {
                "success": True,
                "message": "디바이스 상태 조회 완료",
                "states": self._iot_controller.get_all_states()
            }
        else:
            return {"success": False, "message": f"Unknown tool: {name}"}
    
    def process(self, text: str, context: list[dict] | None = None) -> LLMResponse:
        """Process user input synchronously.
        
        Args:
            text: User input text.
            context: Optional conversation history.
            
        Returns:
            LLM response with text and commands.
        """
        return asyncio.run(self.process_async(text, context))
    
    async def process_async(self, text: str, context: list[dict] | None = None) -> LLMResponse:
        """Process user input asynchronously.
        
        Args:
            text: User input text.
            context: Optional conversation history.
            
        Returns:
            LLM response with text and commands.
        """
        messages = []
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": text})
        
        executed_commands: list[IoTCommand] = []
        
        # Call LLM
        response = await self._async_client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=messages,
            tools=self._tools
        )
        
        # Handle tool use if present
        while response.stop_reason == "tool_use":
            # Find tool use blocks
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            
            # Add assistant message
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute each tool and collect results
            tool_results = []
            for tool_use in tool_uses:
                name = tool_use.name
                arguments = tool_use.input
                
                # Execute tool
                result = await self._execute_tool(name, arguments)
                
                # Record command
                executed_commands.append(IoTCommand(
                    device=name.replace("control_", ""),
                    action=arguments.get("action", "unknown"),
                    parameters=arguments
                ))
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Add tool results
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get next response
            response = await self._async_client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.SYSTEM_PROMPT,
                messages=messages,
                tools=self._tools
            )
        
        # Extract final text response
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break
        
        return LLMResponse(
            text=response_text,
            commands=executed_commands
        )

