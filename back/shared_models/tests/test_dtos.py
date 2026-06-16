from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared_models.dtos import (
    BoardColumnCreateDTO,
    BoardColumnUpdateDTO,
    BoardCreateDTO,
    BoardEventCreateDTO,
    BoardPermissionCreateDTO,
    BoardRowCommentCreateDTO,
    BoardRowCreateDTO,
    BoardRowTaskCreateDTO,
    BoardRowTaskUpdateDTO,
    BoardUpdateDTO,
    UserSearchQueryDTO,
)
from shared_models.dtos.user_dtos import UserInDTO
from shared_models.enums import (
    BoardColumnName,
    BoardFieldType,
    BoardTaskStatus,
    UserRoleInBoard,
)
from shared_models.models.jwt_tokens import JWTTokens


class TestInputDtos:
    def test_board_dtos(self) -> None:
        create_dto = BoardCreateDTO(name="Board")
        update_dto = BoardUpdateDTO(description="Updated")

        assert create_dto.description == ""
        assert update_dto.name is None

    def test_column_dtos(self) -> None:
        board_id = uuid4()
        create_dto = BoardColumnCreateDTO(
            board_id=board_id,
            name=BoardColumnName.TASK_NAME,
            position=0,
        )
        update_dto = BoardColumnUpdateDTO(type=BoardFieldType.DATE)

        assert create_dto.type == BoardFieldType.TEXT
        assert update_dto.position is None

        with pytest.raises(ValidationError):
            BoardColumnCreateDTO(
                board_id=board_id,
                name=BoardColumnName.TASK_NAME,
                position=-1,
            )

    def test_event_permission_row_and_comment_dtos(self) -> None:
        board_id = uuid4()
        row_id = uuid4()
        event = BoardEventCreateDTO(
            board_id=board_id,
            starting_from=date(2026, 1, 1),
            deadline=date(2026, 1, 2),
        )
        permission = BoardPermissionCreateDTO(user_id=uuid4())
        row = BoardRowCreateDTO(board_id=board_id)
        comment = BoardRowCommentCreateDTO(
            board_row_id=row_id,
            content="Comment",
        )

        assert event.description == ""
        assert permission.user_role_in_board == UserRoleInBoard.VIEWER
        assert row.board_id == board_id
        assert comment.board_row_id == row_id

    def test_task_dtos(self) -> None:
        task = BoardRowTaskCreateDTO(
            board_row_id=uuid4(),
            board_column_id=uuid4(),
            task_name="Task",
            deadline=date(2026, 1, 2),
            assigned_to_id=uuid4(),
        )
        update = BoardRowTaskUpdateDTO(version=3)

        assert task.task_status == BoardTaskStatus.PENDING
        assert task.task_content == ""
        assert update.version == 3

    def test_user_dto(self) -> None:
        update = UserInDTO(first_name="Test")

        assert update.email_address is None
        assert update.first_name == "Test"

    def test_search_query_is_normalized(self) -> None:
        assert UserSearchQueryDTO(q="  test  ").q == "test"

        with pytest.raises(ValidationError, match="at least 2 characters"):
            UserSearchQueryDTO(q=" x ")

    def test_jwt_tokens_default_refresh_token(self) -> None:
        tokens = JWTTokens(access_token="access", auth_schema="bearer")

        assert tokens.refresh_token is None
