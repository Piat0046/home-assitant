"""Common data models used across the application."""

from typing import Any

from pydantic import BaseModel, Field


class IoTCommand(BaseModel):
    """Command to be executed on an IoT device."""

    device: str = Field(..., description="Device type (e.g., 'light', 'alarm', 'thermostat')")
    action: str = Field(..., description="Action to perform (e.g., 'on', 'off', 'set')")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class IoTResult(BaseModel):
    """Result of an IoT command execution."""

    success: bool = Field(..., description="Whether the command was successful")
    message: str = Field(..., description="Human-readable result message")
    data: dict[str, Any] = Field(default_factory=dict, description="Additional result data")


class LLMResponse(BaseModel):
    """Response from the LLM."""

    text: str = Field(..., description="Text response to be spoken")
    commands: list[IoTCommand] = Field(default_factory=list, description="IoT commands to execute")


class ChatRequest(BaseModel):
    """Request for chat endpoint."""

    text: str | None = Field(None, description="Text input (for text mode)")
    audio: bytes | None = Field(None, description="Audio input (for audio mode)")
    mode: str = Field("text", description="Input mode: 'text' or 'audio'")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    text: str = Field(..., description="Text response")
    audio: bytes | None = Field(None, description="Audio response (for audio mode)")
    commands_executed: list[IoTResult] = Field(default_factory=list, description="Results of executed commands")
