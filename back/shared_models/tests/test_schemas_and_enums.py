from datetime import date
from uuid import uuid4

from shared_models.enums import (
    AvailabilityStatus,
    BoardColumnName,
    BoardFieldType,
    BoardTaskStatus,
    EnvMode,
    HealthStatus,
    TokenType,
    UserRole,
    UserRoleInBoard,
)
from shared_models.exceptions import ConcurrencyError
from shared_models.models.server_health import ServerHealth
from shared_models.schemas import (
    Board,
    BoardColumn,
    BoardEvent,
    BoardRow,
    BoardRowComment,
    BoardRowTask,
    User,
    UserBoardPermission,
)


class TestEnumsAndModels:
    def test_enum_values(self) -> None:
        assert TokenType.ACCESS == "access"
        assert AvailabilityStatus.AVAILABLE == "available"
        assert HealthStatus.UP == "up"
        assert EnvMode.PROD == "prod"
        assert UserRole.ADMIN == "admin"
        assert UserRoleInBoard.OWNER == "owner"
        assert BoardColumnName.TASK_ID == "TaskID"
        assert BoardFieldType.TEXT == "TEXT"
        assert BoardTaskStatus.COMPLETED == "completed"

    def test_server_health(self) -> None:
        health = ServerHealth(service_name="Service", status=HealthStatus.UP)

        assert health.model_dump(mode="json") == {
            "service_name": "Service",
            "status": "up",
        }

    def test_concurrency_error(self) -> None:
        error = ConcurrencyError("Version mismatch")

        assert str(error) == "Version mismatch"


class TestSchemas:
    def test_schema_defaults_and_relations(self) -> None:
        user_id = uuid4()
        board_id = uuid4()
        row_id = uuid4()
        column_id = uuid4()

        user = User(
            id=user_id,
            email_address="test@example.com",
            password="hashed",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
        )
        board = Board(
            id=board_id,
            name="Board",
            created_by_id=user_id,
        )
        column = BoardColumn(
            id=column_id,
            board_id=board_id,
            name=BoardColumnName.TASK_NAME,
            position=0,
            created_by_id=user_id,
        )
        row = BoardRow(
            id=row_id,
            board_id=board_id,
            created_by_id=user_id,
        )
        task = BoardRowTask(
            board_row_id=row_id,
            board_column_id=column_id,
            task_name="Task",
            deadline=date(2026, 1, 2),
            assigned_to_id=user_id,
            created_by_id=user_id,
        )
        comment = BoardRowComment(
            board_row_id=row_id,
            content="Comment",
            created_by_id=user_id,
        )
        event = BoardEvent(
            board_id=board_id,
            deadline=date(2026, 1, 2),
            created_by_id=user_id,
        )
        permission = UserBoardPermission(user_id=user_id, board_id=board_id)

        assert user.board_relations == []
        assert board.description == ""
        assert board.columns == []
        assert column.type == BoardFieldType.TEXT
        assert row.tasks == []
        assert task.task_status == BoardTaskStatus.PENDING
        assert task.version == 1
        assert comment.content == "Comment"
        assert event.version == 0
        assert permission.user_role_in_board == UserRoleInBoard.VIEWER
