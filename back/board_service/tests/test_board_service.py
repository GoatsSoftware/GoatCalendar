import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from shared_models.dtos.board_in_dtos import BoardCreateDTO, BoardUpdateDTO
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.board_row_in_dtos import BoardRowCreateDTO
from shared_models.dtos.board_row_task_in_dto import BoardRowTaskUpdateDTO
from shared_models.exceptions import ConcurrencyError
from shared_models.schemas import BoardRowTask

from board_service.services import board_row_service, board_service
from tests.constants import BOARD_ID, TASK_ID, USER_ID


class TestBoardService:
    def test_get_all_boards(
        self,
        board: BoardOutDTO,
        session: Mock,
    ) -> None:
        repository_board = Mock()

        with (
            patch.object(
                board_service.board_repository,
                "get_all_boards",
                new=AsyncMock(return_value=[repository_board]),
            ) as repository_mock,
            patch.object(
                board_service,
                "serialize_board_as_dto",
                return_value=board,
            ) as serializer_mock,
        ):
            result = asyncio.run(board_service.get_all_boards(session))

        assert result == [board]
        repository_mock.assert_awaited_once_with(session=session)
        serializer_mock.assert_called_once_with(board=repository_board)

    def test_create_board(
        self,
        board: BoardOutDTO,
        session: Mock,
    ) -> None:
        board_data = BoardCreateDTO(name="Test board", description="Description")
        repository_board = Mock()

        with (
            patch.object(
                board_service.board_repository,
                "create_board",
                new=AsyncMock(return_value=repository_board),
            ) as repository_mock,
            patch.object(
                board_service,
                "serialize_board_as_dto",
                return_value=board,
            ),
        ):
            result = asyncio.run(
                board_service.create_board(board_data, USER_ID, session),
            )

        assert result == board
        repository_mock.assert_awaited_once_with(
            board_data=board_data,
            created_by_id=USER_ID,
            session=session,
        )

    def test_update_board(
        self,
        board: BoardOutDTO,
        session: Mock,
    ) -> None:
        board_data = BoardUpdateDTO(name="Updated board")
        repository_board = Mock()

        with (
            patch.object(
                board_service.board_repository,
                "update_board",
                new=AsyncMock(return_value=repository_board),
            ) as repository_mock,
            patch.object(
                board_service,
                "serialize_board_as_dto",
                return_value=board,
            ),
        ):
            result = asyncio.run(
                board_service.update_board(BOARD_ID, board_data, session),
            )

        assert result == board
        repository_mock.assert_awaited_once_with(
            board_id=BOARD_ID,
            updated_data=board_data,
            session=session,
        )

    def test_delete_board(self, session: Mock) -> None:
        repository_mock = AsyncMock()

        with patch.object(
            board_service.board_repository,
            "delete_board",
            new=repository_mock,
        ):
            asyncio.run(board_service.delete_board(BOARD_ID, session))

        repository_mock.assert_awaited_once_with(
            board_id=BOARD_ID,
            session=session,
        )


class TestBoardRowService:
    def test_create_board_row(self, session: Mock) -> None:
        board_row_data = BoardRowCreateDTO(board_id=BOARD_ID)
        expected_row = Mock()

        with patch.object(
            board_row_service.board_row_repository,
            "create_board_row",
            new=AsyncMock(return_value=expected_row),
        ) as repository_mock:
            result = asyncio.run(
                board_row_service.create_board_row(
                    board_row_data,
                    USER_ID,
                    session,
                ),
            )

        assert result is expected_row
        repository_mock.assert_awaited_once_with(
            board_row_data=board_row_data,
            created_by_id=USER_ID,
            session=session,
        )

    def test_update_board_row_task(self, session: Mock) -> None:
        task_data = BoardRowTaskUpdateDTO(task_name="Updated task", version=4)
        updated_task = Mock(spec=BoardRowTask)

        with patch.object(
            board_row_service.board_row_repository,
            "update_board_row_task_with_version",
            new=AsyncMock(return_value=updated_task),
        ) as repository_mock:
            result = asyncio.run(
                board_row_service.update_board_row_task(
                    TASK_ID,
                    task_data,
                    session,
                ),
            )

        assert result is updated_task
        repository_mock.assert_awaited_once_with(
            task_id=TASK_ID,
            updated_data={"task_name": "Updated task"},
            version_from_client=4,
            session=session,
        )

    def test_update_board_row_task_with_stale_version(self, session: Mock) -> None:
        task_data = BoardRowTaskUpdateDTO(task_name="Updated task", version=4)

        with (
            patch.object(
                board_row_service.board_row_repository,
                "update_board_row_task_with_version",
                new=AsyncMock(return_value=None),
            ),
            pytest.raises(ConcurrencyError, match="Task version mismatch"),
        ):
            asyncio.run(
                board_row_service.update_board_row_task(
                    TASK_ID,
                    task_data,
                    session,
                ),
            )
