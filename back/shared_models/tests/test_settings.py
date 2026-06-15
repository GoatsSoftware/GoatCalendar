from shared_models.enums import EnvMode
from shared_models.models.auth_settings import get_auth_settings
from shared_models.models.db_connection_settings import get_db_connection_settings
from shared_models.models.server_settings import get_server_settings


class TestSettings:
    def test_auth_settings(self, monkeypatch) -> None:
        monkeypatch.setenv("ENCRYPTION_KEY", "secret")
        monkeypatch.setenv("ACCESS_TOKEN_DURATION_MINUTES", "15")
        monkeypatch.setenv("REFRESH_TOKEN_DURATION_HOURS", "24")
        get_auth_settings.cache_clear()

        settings = get_auth_settings()

        assert settings.encryption_key == "secret"
        assert settings.access_token_duration_minutes == 15
        assert settings.refresh_token_duration_hours == 24
        assert get_auth_settings() is settings

    def test_database_settings(self, monkeypatch) -> None:
        monkeypatch.setenv("ENV_MODE", "dev")
        monkeypatch.setenv("DB_DIALECT", "sqlite+aiosqlite")
        monkeypatch.setenv("DB_URL", "database.db")
        get_db_connection_settings.cache_clear()

        settings = get_db_connection_settings()

        assert settings.env_mode == EnvMode.DEV
        assert settings.db_dialect == "sqlite+aiosqlite"
        assert settings.db_url == "database.db"
        assert get_db_connection_settings() is settings

    def test_server_settings(self, monkeypatch) -> None:
        monkeypatch.setenv("FRONT_URL", "http://localhost")
        get_server_settings.cache_clear()

        settings = get_server_settings()

        assert settings.front_url == "http://localhost"
        assert get_server_settings() is settings
