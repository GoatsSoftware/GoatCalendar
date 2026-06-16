import asyncio
from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest
from shared_models.dtos import (
    BoardColumnCreateDTO,
    BoardColumnUpdateDTO,
    BoardCreateDTO,
    BoardEventCreateDTO,
    BoardEventUpdateDTO,
    BoardPermissionUpdateDTO,
    BoardRowCommentCreateDTO,
    BoardRowCommentUpdateDTO,
    BoardRowCreateDTO,
    BoardRowTaskCreateDTO,
    BoardRowTaskUpdateDTO,
    BoardRowUpdateDTO,
    BoardUpdateDTO,
)
from shared_models.enums import (
    BoardColumnName,
    BoardFieldType,
    BoardTaskStatus,
    UserRoleInBoard,
)
from shared_models.schemas import (
    Board,
    BoardColumn,
    BoardEvent,
    BoardRow,
    BoardRowComment,
    BoardRowTask,
    UserBoardPermission,
)
from sqlalchemy.exc import NoResultFound

from board_service.repositories import board_repository, board_row_repository
from tests.constants import BOARD_ID, BOARD_ROW_ID, TASK_ID, USER_ID

COLUMN_ID = TASK_ID
EVENT_ID = TASK_ID
COMMENT_ID = TASK_ID


def query_result(*, one: object | None = None, all_: list | None = None) -> Mock:
    result = Mock()
    result.unique.return_value = result
    result.one.return_value = one
    result.all.return_value = [] if all_ is None else all_
    result.first.return_value = one
    return result


def board_session() -> Mock:
    session = Mock()
    session.exec = AsyncMock()
    session.get = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    return session


class TestBoardRepositoryQueries:
    def test_loading_options(self) -> None:
        assert len(board_repository.get_board_dependencies_loading_options()) == 4
        assert (
            len(board_repository.get_board_column_dependencies_loading_options()) == 1
        )
        assert len(board_repository.get_board_event_dependencies_loading_options()) == 1
        assert (
            len(board_repository.get_board_permission_dependencies_loading_options())
            == 1
        )

    @pytest.mark.parametrize(
        ("repository_method", "expected"),
        [
            (board_repository.get_all_boards, [Mock(spec=Board)]),
            (board_repository.get_user_boards, [Mock(spec=Board)]),
            (board_repository.get_board_columns_by_board_id, [Mock(spec=BoardColumn)]),
            (board_repository.get_board_events_by_board_id, [Mock(spec=BoardEvent)]),
            (
                board_repository.get_board_permissions_by_board_id,
                [Mock(spec=UserBoardPermission)],
            ),
        ],
    )
    def test_list_queries(self, repository_method, expected: list) -> None:
        session = board_session()
        session.exec.return_value = query_result(all_=expected)

        if repository_method is board_repository.get_all_boards:
            result = asyncio.run(repository_method(session))
        else:
            result = asyncio.run(repository_method(BOARD_ID, session))

        assert result == expected
        session.exec.assert_awaited_once()

    @pytest.mark.parametrize(
        ("repository_method", "identifier", "expected"),
        [
            (board_repository.get_board_by_id, BOARD_ID, Mock(spec=Board)),
            (
                board_repository.get_board_column_by_id,
                COLUMN_ID,
                Mock(spec=BoardColumn),
            ),
            (
                board_repository.get_board_event_by_id,
                EVENT_ID,
                Mock(spec=BoardEvent),
            ),
        ],
    )
    def test_get_by_id_queries(
        self,
        repository_method,
        identifier,
        expected: object,
    ) -> None:
        session = board_session()
        session.exec.return_value = query_result(one=expected)

        result = asyncio.run(repository_method(identifier, session))

        assert result is expected
        session.exec.assert_awaited_once()

    def test_get_board_permission(self) -> None:
        session = board_session()
        expected = Mock(spec=UserBoardPermission)
        session.exec.return_value = query_result(one=expected)

        result = asyncio.run(
            board_repository.get_board_permission(BOARD_ID, USER_ID, session),
        )

        assert result is expected


class TestBoardRepositoryCrud:
    def test_create_board(self) -> None:
        session = board_session()
        expected = Mock(spec=Board)
        board_data = BoardCreateDTO(name="Board", description="Description")

        with patch.object(
            board_repository,
            "get_board_by_id",
            new=AsyncMock(return_value=expected),
        ):
            result = asyncio.run(
                board_repository.create_board(board_data, USER_ID, session),
            )

        assert result is expected
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()

    def test_update_and_delete_board(self) -> None:
        session = board_session()
        stored_board = Board(
            id=BOARD_ID,
            name="Old",
            description="Old",
            created_by_id=USER_ID,
        )
        session.get.return_value = stored_board
        expected = Mock(spec=Board)

        with patch.object(
            board_repository,
            "get_board_by_id",
            new=AsyncMock(return_value=expected),
        ):
            result = asyncio.run(
                board_repository.update_board(
                    BOARD_ID,
                    BoardUpdateDTO(name="New"),
                    session,
                ),
            )

        assert result is expected
        assert stored_board.name == "New"

        asyncio.run(board_repository.delete_board(BOARD_ID, session))
        session.delete.assert_awaited_once_with(stored_board)

    @pytest.mark.parametrize(
        "repository_method",
        [board_repository.update_board, board_repository.delete_board],
    )
    def test_board_not_found(self, repository_method) -> None:
        session = board_session()
        session.get.return_value = None

        with pytest.raises(NoResultFound):
            if repository_method is board_repository.update_board:
                asyncio.run(
                    repository_method(
                        BOARD_ID,
                        BoardUpdateDTO(name="New"),
                        session,
                    ),
                )
            else:
                asyncio.run(repository_method(BOARD_ID, session))

    def test_column_crud(self) -> None:
        session = board_session()
        column_data = BoardColumnCreateDTO(
            board_id=BOARD_ID,
            name=BoardColumnName.TASK_NAME,
            type=BoardFieldType.TEXT,
            position=1,
        )
        expected = Mock(spec=BoardColumn)

        with patch.object(
            board_repository,
            "get_board_column_by_id",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_repository.create_board_column(column_data, USER_ID, session),
            )

            stored_column = BoardColumn(
                id=COLUMN_ID,
                board_id=BOARD_ID,
                name=BoardColumnName.TASK_NAME,
                type=BoardFieldType.TEXT,
                position=1,
                created_by_id=USER_ID,
            )
            session.get.return_value = stored_column
            updated = asyncio.run(
                board_repository.update_board_column(
                    COLUMN_ID,
                    BoardColumnUpdateDTO(position=2),
                    session,
                ),
            )

        assert created is expected
        assert updated is expected
        assert stored_column.position == 2

        session.execute.return_value = Mock(rowcount=1)
        asyncio.run(board_repository.delete_board_column(COLUMN_ID, session))

    def test_column_not_found(self) -> None:
        session = board_session()
        session.get.return_value = None
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_repository.update_board_column(
                    COLUMN_ID,
                    BoardColumnUpdateDTO(position=2),
                    session,
                ),
            )

        session.execute.return_value = Mock(rowcount=0)
        with pytest.raises(NoResultFound):
            asyncio.run(board_repository.delete_board_column(COLUMN_ID, session))

    def test_event_crud(self) -> None:
        session = board_session()
        event_data = BoardEventCreateDTO(
            board_id=BOARD_ID,
            title="Milestone",
            starting_from=date(2026, 1, 1),
            deadline=date(2026, 1, 2),
        )
        expected = Mock(spec=BoardEvent)

        with patch.object(
            board_repository,
            "get_board_event_by_id",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_repository.create_board_event(event_data, USER_ID, session),
            )

            stored_event = BoardEvent(
                id=EVENT_ID,
                board_id=BOARD_ID,
                title="Milestone",
                deadline=date(2026, 1, 2),
                created_by_id=USER_ID,
            )
            session.get.return_value = stored_event
            updated = asyncio.run(
                board_repository.update_board_event(
                    EVENT_ID,
                    BoardEventUpdateDTO(title="Updated"),
                    session,
                ),
            )

        assert created is expected
        assert updated is expected
        assert stored_event.title == "Updated"

        session.execute.return_value = Mock(rowcount=1)
        asyncio.run(board_repository.delete_board_event(EVENT_ID, session))

    def test_event_not_found(self) -> None:
        session = board_session()
        session.get.return_value = None
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_repository.update_board_event(
                    EVENT_ID,
                    BoardEventUpdateDTO(title="Updated"),
                    session,
                ),
            )

        session.execute.return_value = Mock(rowcount=0)
        with pytest.raises(NoResultFound):
            asyncio.run(board_repository.delete_board_event(EVENT_ID, session))

    def test_permission_crud(self) -> None:
        session = board_session()
        permission_data = {
            "board_id": BOARD_ID,
            "user_id": USER_ID,
            "user_role_in_board": UserRoleInBoard.EDITOR,
        }
        expected = Mock(spec=UserBoardPermission)

        with patch.object(
            board_repository,
            "get_board_permission",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_repository.add_user_to_board(permission_data, session),
            )

            stored_permission = UserBoardPermission(
                board_id=BOARD_ID,
                user_id=USER_ID,
                user_role_in_board=UserRoleInBoard.VIEWER,
            )
            session.exec.return_value = query_result(one=stored_permission)
            updated = asyncio.run(
                board_repository.update_user_board_permission(
                    BOARD_ID,
                    USER_ID,
                    BoardPermissionUpdateDTO(
                        user_role_in_board=UserRoleInBoard.EDITOR,
                    ),
                    session,
                ),
            )

        assert created is expected
        assert updated is expected
        assert stored_permission.user_role_in_board == UserRoleInBoard.EDITOR

        session.execute.return_value = Mock(rowcount=1)
        asyncio.run(
            board_repository.remove_user_from_board(BOARD_ID, USER_ID, session),
        )

    def test_permission_not_found(self) -> None:
        session = board_session()
        session.exec.return_value = query_result()
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_repository.update_user_board_permission(
                    BOARD_ID,
                    USER_ID,
                    BoardPermissionUpdateDTO(
                        user_role_in_board=UserRoleInBoard.EDITOR,
                    ),
                    session,
                ),
            )

        session.execute.return_value = Mock(rowcount=0)
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_repository.remove_user_from_board(BOARD_ID, USER_ID, session),
            )


class TestBoardRowRepository:
    def test_loading_options(self) -> None:
        assert (
            len(board_row_repository.get_board_row_dependencies_loading_options()) == 3
        )
        assert (
            len(board_row_repository.get_board_row_task_dependencies_loading_options())
            == 3
        )
        assert (
            len(
                board_row_repository.get_board_row_comment_dependencies_loading_options(),
            )
            == 1
        )

    @pytest.mark.parametrize(
        ("repository_method", "identifier", "expected"),
        [
            (
                board_row_repository.get_board_row_by_id,
                BOARD_ROW_ID,
                Mock(spec=BoardRow),
            ),
            (
                board_row_repository.get_board_row_task_by_id,
                TASK_ID,
                Mock(spec=BoardRowTask),
            ),
            (
                board_row_repository.get_board_row_comment_by_id,
                COMMENT_ID,
                Mock(spec=BoardRowComment),
            ),
        ],
    )
    def test_get_by_id(self, repository_method, identifier, expected: object) -> None:
        session = board_session()
        session.exec.return_value = query_result(one=expected)

        result = asyncio.run(repository_method(identifier, session))

        assert result is expected

    @pytest.mark.parametrize(
        ("repository_method", "identifier", "expected"),
        [
            (
                board_row_repository.get_board_rows_by_board_id,
                BOARD_ID,
                [Mock(spec=BoardRow)],
            ),
            (
                board_row_repository.get_board_row_tasks_by_board_row_id,
                BOARD_ROW_ID,
                [Mock(spec=BoardRowTask)],
            ),
            (
                board_row_repository.get_board_row_tasks_by_board_column_id,
                COLUMN_ID,
                [Mock(spec=BoardRowTask)],
            ),
            (
                board_row_repository.get_board_row_comments_by_board_row_id,
                BOARD_ROW_ID,
                [Mock(spec=BoardRowComment)],
            ),
        ],
    )
    def test_list_queries(self, repository_method, identifier, expected: list) -> None:
        session = board_session()
        session.exec.return_value = query_result(all_=expected)

        result = asyncio.run(repository_method(identifier, session))

        assert result == expected

    def test_board_row_crud(self) -> None:
        session = board_session()
        expected = Mock(spec=BoardRow)

        with patch.object(
            board_row_repository,
            "get_board_row_by_id",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_row_repository.create_board_row(
                    BoardRowCreateDTO(board_id=BOARD_ID),
                    USER_ID,
                    session,
                ),
            )

            stored_row = BoardRow(
                id=BOARD_ROW_ID,
                board_id=BOARD_ID,
                created_by_id=USER_ID,
            )
            session.get.return_value = stored_row
            updated = asyncio.run(
                board_row_repository.update_board_row(
                    BOARD_ROW_ID,
                    BoardRowUpdateDTO(board_id=BOARD_ID),
                    session,
                ),
            )

        assert created is expected
        assert updated is expected
        asyncio.run(board_row_repository.delete_board_row(BOARD_ROW_ID, session))
        session.delete.assert_awaited_once_with(stored_row)

    def test_board_row_not_found(self) -> None:
        session = board_session()
        session.get.return_value = None

        with pytest.raises(NoResultFound):
            asyncio.run(
                board_row_repository.update_board_row(
                    BOARD_ROW_ID,
                    BoardRowUpdateDTO(board_id=BOARD_ID),
                    session,
                ),
            )

        with pytest.raises(NoResultFound):
            asyncio.run(
                board_row_repository.delete_board_row(BOARD_ROW_ID, session),
            )

    def test_task_crud_and_versioning(self) -> None:
        session = board_session()
        expected = Mock(spec=BoardRowTask)
        task_data = BoardRowTaskCreateDTO(
            board_row_id=BOARD_ROW_ID,
            board_column_id=COLUMN_ID,
            task_name="Task",
            deadline=date(2026, 1, 2),
            assigned_to_id=USER_ID,
        )

        with patch.object(
            board_row_repository,
            "get_board_row_task_by_id",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_row_repository.create_board_row_task(
                    task_data,
                    USER_ID,
                    session,
                ),
            )
            session.execute.return_value = Mock(rowcount=1)
            updated = asyncio.run(
                board_row_repository.update_board_row_task_with_version(
                    TASK_ID,
                    BoardRowTaskUpdateDTO(
                        task_status=BoardTaskStatus.COMPLETED,
                        version=1,
                    ).model_dump(exclude={"version"}, exclude_none=True),
                    1,
                    session,
                ),
            )

        assert created is expected
        assert updated is expected

        session.execute.return_value = Mock(rowcount=0)
        assert (
            asyncio.run(
                board_row_repository.update_board_row_task_with_version(
                    TASK_ID,
                    {},
                    1,
                    session,
                ),
            )
            is None
        )

        asyncio.run(board_row_repository.delete_board_row_task(TASK_ID, session))

    def test_comment_crud(self) -> None:
        session = board_session()
        expected = Mock(spec=BoardRowComment)

        with patch.object(
            board_row_repository,
            "get_board_row_comment_by_id",
            new=AsyncMock(return_value=expected),
        ):
            created = asyncio.run(
                board_row_repository.create_board_row_comment(
                    BoardRowCommentCreateDTO(
                        board_row_id=BOARD_ROW_ID,
                        content="Comment",
                    ),
                    USER_ID,
                    session,
                ),
            )

            stored_comment = BoardRowComment(
                id=COMMENT_ID,
                board_row_id=BOARD_ROW_ID,
                content="Comment",
                created_by_id=USER_ID,
            )
            session.get.return_value = stored_comment
            updated = asyncio.run(
                board_row_repository.update_board_row_comment(
                    COMMENT_ID,
                    BoardRowCommentUpdateDTO(content="Updated"),
                    session,
                ),
            )

        assert created is expected
        assert updated is expected
        assert stored_comment.content == "Updated"

        session.execute.return_value = Mock(rowcount=1)
        asyncio.run(
            board_row_repository.delete_board_row_comment(COMMENT_ID, session),
        )

    def test_comment_not_found(self) -> None:
        session = board_session()
        session.get.return_value = None
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_row_repository.update_board_row_comment(
                    COMMENT_ID,
                    BoardRowCommentUpdateDTO(content="Updated"),
                    session,
                ),
            )

        session.execute.return_value = Mock(rowcount=0)
        with pytest.raises(NoResultFound):
            asyncio.run(
                board_row_repository.delete_board_row_comment(COMMENT_ID, session),
            )
