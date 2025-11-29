"""OpenAI LLM implementation."""

import asyncio
import json
from typing import Any, Optional

from openai import OpenAI, AsyncOpenAI

from home_ai.common.models import LLMResponse, IoTCommand
from home_ai.mcp_iot.server import IoTController


class OpenAILLM:
    """LLM using OpenAI GPT models with function calling.
    
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
        model: str = "gpt-4o-mini",
        iot_controller: Optional[IoTController] = None,
    ):
        """Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key.
            model: Model to use.
            iot_controller: IoT controller for device control.
        """
        self.model = model
        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)
        self._iot_controller = iot_controller or IoTController()
        self._tools = self._create_tools()
    
    def _create_tools(self) -> list[dict[str, Any]]:
        """Create OpenAI function definitions from IoT controller."""
        iot_tools = self._iot_controller.get_tools()
        
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
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
    
    # Alias for testing
    @property
    def _tool_executor(self):
        return self._execute_tool
    
    @_tool_executor.setter
    def _tool_executor(self, value):
        self._execute_tool = value
    
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
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": text})
        
        executed_commands: list[IoTCommand] = []
        
        # Call LLM
        response = await self._async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._tools,
            tool_choice="auto"
        )
        
        choice = response.choices[0]
        
        # Handle tool calls if present
        while choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": choice.message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in choice.message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Execute tool
                result = await self._execute_tool(name, arguments)
                
                # Record command
                executed_commands.append(IoTCommand(
                    device=name.replace("control_", ""),
                    action=arguments.get("action", "unknown"),
                    parameters=arguments
                ))
                
                # Add tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Get next response
            response = await self._async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._tools,
                tool_choice="auto"
            )
            choice = response.choices[0]
        
        # Extract final text response
        response_text = choice.message.content or ""
        
        return LLMResponse(
            text=response_text,
            commands=executed_commands
        )

