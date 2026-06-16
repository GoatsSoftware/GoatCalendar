import asyncio
from contextlib import suppress
from unittest.mock import AsyncMock, Mock, patch

import main


class TestMain:
    def test_seed_db(self) -> None:
        engine = Mock()
        engine.dispose = AsyncMock()

        with (
            patch.object(
                main,
                "create_db_and_tables",
                new=AsyncMock(),
            ) as create_mock,
            patch.object(main, "base_seeder", new=AsyncMock()) as seeder_mock,
            patch.object(main, "engine", engine),
        ):
            asyncio.run(main.seed_db())

        create_mock.assert_awaited_once()
        seeder_mock.assert_awaited_once()
        engine.dispose.assert_awaited_once()

    def test_seed_db_disposes_engine_after_failure(self) -> None:
        engine = Mock()
        engine.dispose = AsyncMock()

        with (
            patch.object(
                main,
                "create_db_and_tables",
                new=AsyncMock(side_effect=RuntimeError("Failed")),
            ),
            patch.object(main, "engine", engine),
            suppress(RuntimeError),
        ):
            asyncio.run(main.seed_db())

        engine.dispose.assert_awaited_once()
