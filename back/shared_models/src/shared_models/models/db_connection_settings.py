from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_models.enums import EnvMode


class DbConnectionSettings(BaseSettings):
    """
    Configuration settings for database connectivity.

    This class automatically loads variables from environment variables or
    specified .env files using Pydantic Settings.
    """

    env_mode: EnvMode = Field(validation_alias="ENV_MODE")
    db_dialect: str = Field(validation_alias="DB_DIALECT")
    db_url: str | None = Field(default=None, validation_alias="DB_URL")

    model_config = SettingsConfigDict(
        env_file=(".env.prod", ".env"),
        extra="ignore",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_db_connection_settings() -> "DbConnectionSettings":
    """
    Retrieve a cached instance of the database connection settings.

    Uses LRU (Least Recently Used) caching to ensure the settings are
    initialized only once during the application lifecycle, improving
    performance for repeated dependency injections.

    :return: An initialized DbConnectionSettings object.
    """
    return DbConnectionSettings()
