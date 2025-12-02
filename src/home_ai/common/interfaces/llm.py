"""LLM interface protocol."""

from typing import Protocol, runtime_checkable

from home_ai.common.models import LLMResponse


@runtime_checkable
class LLMInterface(Protocol):
    """Protocol for LLM implementations.

    All LLM implementations should conform to this interface.
    The LLM processes user input and returns responses with optional IoT commands.
    """

    def process(self, text: str, context: list[dict] | None = None) -> LLMResponse:
        """Process user input and generate a response.

        Args:
            text: User input text.
            context: Optional conversation history for context.

        Returns:
            LLMResponse containing text response and any IoT commands.
        """
        ...

    async def process_async(self, text: str, context: list[dict] | None = None) -> LLMResponse:
        """Asynchronously process user input and generate a response.

        Args:
            text: User input text.
            context: Optional conversation history for context.

        Returns:
            LLMResponse containing text response and any IoT commands.
        """
        ...
