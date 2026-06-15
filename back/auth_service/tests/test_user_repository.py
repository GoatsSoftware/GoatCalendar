import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from shared_models.dtos.user_dtos import UserInDTO
from shared_models.schemas import User
from sqlalchemy.exc import NoResultFound

from auth_service.repositories import user_repository
from tests.constants import EMAIL, USER_ID


def query_result(*, one: object | None = None, all_: list | None = None) -> Mock:
    result = Mock()
    result.unique.return_value = result
    result.one.return_value = one
    result.all.return_value = [] if all_ is None else all_
    return result


class TestUserRepository:
    def test_get_all_users(self, user: User) -> None:
        session = Mock()
        session.exec = AsyncMock(return_value=query_result(all_=[user]))

        result = asyncio.run(user_repository.get_all_users(session))

        assert result == [user]

    def test_get_user_by_email_address(self, user: User) -> None:
        session = Mock()
        session.exec = AsyncMock(return_value=query_result(one=user))

        result = asyncio.run(
            user_repository.get_user_by_email_address(EMAIL, session),
        )

        assert result is user

    def test_search_users(self, user: User) -> None:
        session = Mock()
        session.exec = AsyncMock(return_value=query_result(all_=[user]))

        result = asyncio.run(user_repository.search_users("test", session))

        assert result == [user]

    def test_update_user(self, user: User) -> None:
        session = Mock()
        session.get = AsyncMock(return_value=user)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        update_data = UserInDTO(first_name="Updated")

        result = asyncio.run(
            user_repository.update_user(USER_ID, update_data, session),
        )

        assert result is user
        assert user.first_name == "Updated"
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(user)

    def test_update_user_not_found(self) -> None:
        session = Mock()
        session.get = AsyncMock(return_value=None)

        with pytest.raises(NoResultFound):
            asyncio.run(
                user_repository.update_user(
                    USER_ID,
                    UserInDTO(first_name="Updated"),
                    session,
                ),
            )
