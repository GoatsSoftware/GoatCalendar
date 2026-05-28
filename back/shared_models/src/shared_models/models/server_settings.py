from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """ """

    front_url: str = Field(
        validation_alias="FRONT_URL",
    )

    model_config = SettingsConfigDict(
        env_file=(".env.prod", ".env"),
        extra="ignore",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_server_settings() -> "ServerSettings":
    """
    Returns a cached instance of the server configuration.

    Leveraging the LRU cache prevents the application from re-reading
    environment files and re-running Pydantic validation on every
    request/call. This maintains a single source of truth for server
    parameters throughout the process lifecycle.

    :return: A singleton instance of the ServerSettings class.
    """
    return ServerSettings()
