"""Configuration management for the application."""

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings.

    All settings can be overridden by environment variables with the prefix APP_.
    For example, APP_LOG_LEVEL=DEBUG will set log_level to DEBUG.
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API settings
    api_title: str = "Swiss Parking Spaces API"
    api_description: str = "API for retrieving parking spaces availability in Swiss cities"
    api_version: str = "0.1.0"
    api_root_path: str = ""

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000

    # Cache settings
    cache_ttl: int = Field(
        default=60,
        description="Time to live for cached data in seconds",
    )

    # Logging settings
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Data source settings
    request_timeout: int = Field(
        default=10,
        description="Timeout for HTTP requests in seconds",
    )


@lru_cache
def get_settings() -> Settings:
    """Get application settings singleton.

    Returns:
        Settings: Application settings
    """
    return Settings()
