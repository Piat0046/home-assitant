"""Application configuration using pydantic-settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # MCP IoT Server settings
    mcp_iot_host: str = "localhost"
    mcp_iot_port: int = 8001

    # Database settings
    database_url: str = "postgresql://home_ai:password@localhost:5432/home_ai"

    # API Keys (optional, loaded from environment)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_dir: str = "./logs"

    # Provider settings
    stt_provider: Literal["google", "openai"] = "google"
    tts_provider: Literal["gtts", "openai"] = "gtts"
    llm_provider: Literal["openai", "claude"] = "openai"


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings instance (singleton).
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
