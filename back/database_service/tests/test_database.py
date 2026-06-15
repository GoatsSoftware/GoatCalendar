import asyncio
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy.exc import SQLAlchemyError

from database_service import database


class AsyncContextManager:
    def __init__(self, value=None, error: Exception | None = None) -> None:
        self.value = value
        self.error = error

    async def __aenter__(self):
        if self.error is not None:
            raise self.error
        return self.value

    async def __aexit__(self, *_args) -> None:
        return None


class TestDatabase:
    def test_create_db_and_tables(self) -> None:
        connection = Mock()
        connection.run_sync = AsyncMock()
        engine = Mock()
        engine.begin.return_value = AsyncContextManager(connection)

        with patch.object(database, "engine", engine):
            asyncio.run(database.create_db_and_tables())

        connection.run_sync.assert_awaited_once_with(
            database.SQLModel.metadata.create_all,
        )

    def test_create_db_and_tables_retries(self) -> None:
        connection = Mock()
        connection.run_sync = AsyncMock()
        engine = Mock()
        engine.begin.side_effect = [
            AsyncContextManager(error=SQLAlchemyError("Unavailable")),
            AsyncContextManager(connection),
        ]

        with (
            patch.object(database, "engine", engine),
            patch.object(database, "sleep", new=AsyncMock()) as sleep_mock,
        ):
            asyncio.run(database.create_db_and_tables())

        assert engine.begin.call_count == 2
        sleep_mock.assert_awaited_once_with(database.retry_interval)

    def test_create_db_and_tables_stops_after_max_retries(self) -> None:
        engine = Mock()
        engine.begin.return_value = AsyncContextManager(
            error=SQLAlchemyError("Unavailable"),
        )

        with (
            patch.object(database, "engine", engine),
            patch.object(database, "sleep", new=AsyncMock()) as sleep_mock,
        ):
            asyncio.run(
                database.create_db_and_tables(database.max_db_conn_retries),
            )

        sleep_mock.assert_not_awaited()

    def test_get_db_session(self) -> None:
        session = Mock()

        with patch.object(
            database,
            "AsyncSession",
            return_value=AsyncContextManager(session),
        ):

            async def get_session():
                generator = database.get_db_session()
                yielded_session = await anext(generator)
                await generator.aclose()
                return yielded_session

            result = asyncio.run(get_session())

        assert result is session
