from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.board_row_out_dto import BoardRowOutDTO
from shared_models.exceptions import ConcurrencyError
from sqlalchemy.exc import NoResultFound

from tests.constants import BOARD_ID, BOARD_ROW_ID, TASK_ID, USER_ID


class TestBoardRoutes:
    def test_get_all_boards(
        self,
        client: TestClient,
        board: BoardOutDTO,
    ) -> None:
        with patch(
            "board_service.services.board_service.get_all_boards",
            new=AsyncMock(return_value=[board]),
        ):
            response = client.get("/boards")

        assert response.status_code == 200
        assert response.json() == [board.model_dump(mode="json")]

    def test_get_board_by_id_found(
        self,
        client: TestClient,
        board: BoardOutDTO,
    ) -> None:
        with patch(
            "board_service.services.board_service.get_board_by_id",
            new=AsyncMock(return_value=board),
        ):
            response = client.get(f"/boards/{BOARD_ID}")

        assert response.status_code == 200
        assert response.json() == board.model_dump(mode="json")

    def test_get_board_by_id_not_found(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_service.get_board_by_id",
            new=AsyncMock(side_effect=NoResultFound),
        ):
            response = client.get(f"/boards/{BOARD_ID}")

        assert response.status_code == 404
        assert response.json() == {"detail": f"Board '{BOARD_ID}' not found"}

    def test_create_board(
        self,
        client: TestClient,
        board: BoardOutDTO,
    ) -> None:
        service_mock = AsyncMock(return_value=board)

        with patch(
            "board_service.services.board_service.create_board",
            new=service_mock,
        ):
            response = client.post(
                "/boards",
                json={"name": "Test board", "description": "Board used by tests"},
            )

        assert response.status_code == 201
        assert response.json() == board.model_dump(mode="json")
        assert service_mock.await_args.kwargs["created_by_id"] == USER_ID

    def test_update_board(
        self,
        client: TestClient,
        board: BoardOutDTO,
    ) -> None:
        with patch(
            "board_service.services.board_service.update_board",
            new=AsyncMock(return_value=board),
        ):
            response = client.put(
                f"/boards/{BOARD_ID}",
                json={"name": "Updated board"},
            )

        assert response.status_code == 200
        assert response.json() == board.model_dump(mode="json")

    def test_delete_board(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_service.delete_board",
            new=AsyncMock(),
        ):
            response = client.delete(f"/boards/{BOARD_ID}")

        assert response.status_code == 204
        assert response.content == b""


class TestBoardRowRoutes:
    def test_get_board_row_by_id(
        self,
        client: TestClient,
        board_row: BoardRowOutDTO,
    ) -> None:
        with patch(
            "board_service.services.board_row_service.get_board_row_by_id",
            new=AsyncMock(return_value=board_row),
        ):
            response = client.get(f"/board-rows/{BOARD_ROW_ID}")

        assert response.status_code == 200
        assert response.json() == board_row.model_dump(mode="json")

    def test_create_board_row(
        self,
        client: TestClient,
        board_row: BoardRowOutDTO,
    ) -> None:
        service_mock = AsyncMock(return_value=board_row)

        with patch(
            "board_service.services.board_row_service.create_board_row",
            new=service_mock,
        ):
            response = client.post(
                "/board-rows",
                json={"board_id": str(BOARD_ID)},
            )

        assert response.status_code == 201
        assert response.json() == board_row.model_dump(mode="json")
        assert service_mock.await_args.kwargs["created_by_id"] == USER_ID

    def test_update_board_row_not_found(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_row_service.update_board_row",
            new=AsyncMock(side_effect=NoResultFound),
        ):
            response = client.put(
                f"/board-rows/{BOARD_ROW_ID}",
                json={"board_id": str(BOARD_ID)},
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": f"Board row '{BOARD_ROW_ID}' not found",
        }

    def test_delete_board_row(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_row_service.delete_board_row",
            new=AsyncMock(),
        ):
            response = client.delete(f"/board-rows/{BOARD_ROW_ID}")

        assert response.status_code == 204
        assert response.content == b""


class TestBoardRowTaskRoutes:
    def test_update_task_with_stale_version(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_row_service.update_board_row_task",
            new=AsyncMock(side_effect=ConcurrencyError("Task version mismatch")),
        ):
            response = client.put(
                f"/board-row-tasks/{TASK_ID}",
                json={"task_name": "Updated task", "version": 2},
            )

        assert response.status_code == 409
        assert response.json() == {
            "detail": (
                "This task has been modified by another user. Please refresh the board."
            ),
        }

    def test_get_task_not_found(self, client: TestClient) -> None:
        with patch(
            "board_service.services.board_row_service.get_board_row_task_by_id",
            new=AsyncMock(side_effect=NoResultFound),
        ):
            response = client.get(f"/board-row-tasks/{TASK_ID}")

        assert response.status_code == 404
        assert response.json() == {"detail": f"Task '{TASK_ID}' not found"}
