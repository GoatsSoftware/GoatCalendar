import asyncio
from datetime import UTC
from unittest.mock import AsyncMock, Mock, patch

from shared_models.enums import UserRoleInBoard

from database_service import seeder


class AsyncContextManager:
    def __init__(self, value) -> None:
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, *_args) -> None:
        return None


def fake_session() -> Mock:
    session = Mock()
    session.add = Mock()
    session.add_all = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


class TestSeeder:
    def test_seed_users(self) -> None:
        session = fake_session()

        users = asyncio.run(seeder.seed_users(session))

        assert len(users) == 3
        assert [user.email_address for user in users] == [
            seeder.ALICE_EMAIL,
            seeder.BOB_EMAIL,
            seeder.CLAIRE_EMAIL,
        ]
        session.add_all.assert_called_once_with(users)
        session.flush.assert_awaited_once()

    def test_seed_board_structure(self) -> None:
        session = fake_session()
        users = asyncio.run(seeder.seed_users(session))
        session.add_all.reset_mock()
        session.flush.reset_mock()

        with patch.object(seeder, "ZoneInfo", return_value=UTC):
            board = asyncio.run(seeder.seed_board_structure(session, users))

        assert board.name == "Demo Board"
        assert board.created_by_id == users[0].id
        assert session.add.call_count == 11
        assert session.add_all.call_count == 4

        columns = session.add_all.call_args_list[0].args[0]
        tasks = session.add_all.call_args_list[1].args[0]
        events = session.add_all.call_args_list[2].args[0]
        permissions = session.add_all.call_args_list[3].args[0]

        assert len(columns) == 5
        assert len(tasks) == 25
        assert len(events) == 2
        assert len(permissions) == 2
        assert permissions[0].user_role_in_board == UserRoleInBoard.EDITOR
        assert permissions[1].user_role_in_board == UserRoleInBoard.VIEWER
        assert session.flush.await_count == 9

    def test_base_seeder(self) -> None:
        session = fake_session()
        users = [Mock(), Mock(), Mock()]

        with (
            patch.object(
                seeder,
                "AsyncSession",
                return_value=AsyncContextManager(session),
            ),
            patch.object(
                seeder,
                "seed_users",
                new=AsyncMock(return_value=users),
            ) as seed_users_mock,
            patch.object(
                seeder,
                "seed_board_structure",
                new=AsyncMock(),
            ) as seed_board_mock,
        ):
            asyncio.run(seeder.base_seeder())

        seed_users_mock.assert_awaited_once_with(session)
        seed_board_mock.assert_awaited_once_with(session, users)
        session.commit.assert_awaited_once()
