from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """
    Validates and stores the configuration for JWT operations and encryption.

    This model automatically maps environment variables from .env files to
    strongly typed attributes. It enforces the presence of critical security
    keys and provides the foundation for signed token generation.
    """

    encryption_key: str = Field(validation_alias="ENCRYPTION_KEY")
    access_token_duration_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_DURATION_MINUTES",
    )
    refresh_token_duration_hours: int = Field(
        validation_alias="REFRESH_TOKEN_DURATION_HOURS",
    )

    model_config = SettingsConfigDict(
        env_file=(".env.prod", ".env"),
        extra="ignore",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_auth_settings() -> "AuthSettings":
    """
    Provides a memoized instance of the authentication settings.

    This function uses a Least Recently Used (LRU) cache to ensure the
    configuration is only loaded and validated once during the application
    lifecycle. Subsequent calls return the cached object, improving
    performance by avoiding repeated file I/O operations.

    :return: A singleton instance of the AuthSettings class.
    """
    return AuthSettings()
