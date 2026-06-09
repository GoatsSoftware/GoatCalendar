from uuid import UUID

from shared_models.dtos.board_row_in_dtos import BoardRowCreateDTO, BoardRowUpdateDTO
from shared_models.dtos.board_row_comment_in_dto import (
    BoardRowCommentCreateDTO,
    BoardRowCommentUpdateDTO,
)
from shared_models.schemas import BoardRow, BoardRowComment, BoardRowTask
from shared_models.exceptions import ConcurrencyException
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_row_repository
from shared_models.dtos.board_row_task_in_dto import (
    BoardRowTaskCreateDTO,
    BoardRowTaskUpdateDTO,
)


async def get_board_row_by_id(board_row_id: UUID, session: AsyncSession) -> BoardRow:
    """
    Business service layer to retrieve a specific board row by its ID.

    :param board_row_id: The UUID of the row.
    :param session: The active database session.
    :return: The matching BoardRow model record.
    """
    return await board_row_repository.get_board_row_by_id(
        board_row_id=board_row_id,
        session=session,
    )


async def get_board_rows_by_board_id(
    board_id: UUID,
    session: AsyncSession,
) -> list[BoardRow]:
    """
    Business service layer to retrieve all rows belonging to a single board.

    :param board_id: The UUID of the board container.
    :param session: The active database session.
    :return: A list of matching BoardRow model records.
    """
    return await board_row_repository.get_board_rows_by_board_id(
        board_id=board_id,
        session=session,
    )


async def create_board_row(
    board_row_data: BoardRowCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRow:
    """
    Create a new row inside a board.

    :param board_row_data: The validated payload describing the new row.
    :param created_by_id: The UUID of the authenticated creator.
    :param session: The active database session.
    :return: The newly created board row model.
    """
    board_row_payload = board_row_data.model_dump(exclude_none=True)
    board_row_payload["created_by_id"] = created_by_id
    return await board_row_repository.create_board_row(
        board_row_payload,
        session=session,
    )


async def update_board_row(
    board_row_id: UUID,
    board_row_data: BoardRowUpdateDTO,
    session: AsyncSession,
) -> BoardRow:
    """
    Update a board row's properties.

    :param board_row_id: The UUID of the row to update.
    :param board_row_data: The validated payload containing new row values.
    :param session: The active database session.
    :return: The updated board row model.
    """
    return await board_row_repository.update_board_row(
        board_row_id=board_row_id,
        updated_data=board_row_data.model_dump(exclude_none=True),
        session=session,
    )


async def delete_board_row(board_row_id: UUID, session: AsyncSession) -> None:
    """
    Delete a board row by its identifier.

    :param board_row_id: The UUID of the row to delete.
    :param session: The active database session.
    :return: None.
    """
    await board_row_repository.delete_board_row(
        board_row_id=board_row_id,
        session=session,
    )


async def create_board_row_task(
    task_data: BoardRowTaskCreateDTO, created_by_id: UUID, session: AsyncSession
) -> BoardRowTask:
    """
    Create a new task inside a board row.

    :param task_data: The validated payload used to create the task.
    :param created_by_id: The UUID of the authenticated creator.
    :param session: The active database session.
    :return: The fully loaded created task model.
    """
    task_payload = task_data.model_dump(exclude_none=True)
    task_payload["created_by_id"] = created_by_id
    task_payload["version"] = 1
    task = await board_row_repository.create_board_row_task(
        task_payload,
        session=session,
    )
    return await board_row_repository.get_board_row_task_by_id(
        task_id=task.id,
        session=session,
    )


async def get_board_row_task_by_id(task_id: UUID, session: AsyncSession) -> BoardRowTask:
    """
    Retrieve a single board row task by its identifier.

    :param task_id: The UUID of the task to retrieve.
    :param session: The active database session.
    :return: The matching task model.
    """
    return await board_row_repository.get_board_row_task_by_id(
        task_id=task_id,
        session=session,
    )


async def get_board_row_tasks_by_board_row_id(
    board_row_id: UUID, session: AsyncSession
) -> list[BoardRowTask]:
    """
    Retrieve all tasks belonging to a board row.

    :param board_row_id: The UUID of the parent board row.
    :param session: The active database session.
    :return: A list of matching task models.
    """
    return await board_row_repository.get_board_row_tasks_by_board_row_id(
        board_row_id=board_row_id,
        session=session,
    )


async def get_board_row_tasks_by_board_column_id(
    board_column_id: UUID, session: AsyncSession
) -> list[BoardRowTask]:
    """
    Retrieve all tasks associated with a board column.

    :param board_column_id: The UUID of the board column.
    :param session: The active database session.
    :return: A list of matching task models.
    """
    return await board_row_repository.get_board_row_tasks_by_board_column_id(
        board_column_id=board_column_id,
        session=session,
    )


async def update_board_row_task(
    task_id: UUID, task_data: BoardRowTaskUpdateDTO, session: AsyncSession
) -> BoardRowTask:
    """
    Update an existing task using optimistic locking.

    :param task_id: The UUID of the task to update.
    :param task_data: The validated payload containing updated task values.
    :param session: The active database session.
    :return: The updated task model.
    :raises ConcurrencyException: If the client version is stale.
    """
    task_payload = task_data.model_dump(exclude_none=True)
    version_from_client = task_payload.pop("version")

    updated_task = await board_row_repository.update_board_row_task_with_version(
        task_id=task_id,
        updated_data=task_payload,
        version_from_client=version_from_client,
        session=session,
    )

    if updated_task is None:
        raise ConcurrencyException("Task version mismatch")

    return updated_task


async def delete_board_row_task(task_id: UUID, session: AsyncSession) -> None:
    """
    Delete a task by its identifier.

    :param task_id: The UUID of the task to delete.
    :param session: The active database session.
    :return: None.
    """
    await board_row_repository.delete_board_row_task(task_id=task_id, session=session)


async def create_board_row_comment(
    comment_data: BoardRowCommentCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRowComment:
    """
    Create a new comment on a board row.

    :param comment_data: The validated payload describing the new comment.
    :param created_by_id: The UUID of the authenticated creator.
    :param session: The active database session.
    :return: The newly created comment model.
    """
    comment_payload = comment_data.model_dump(exclude_none=True)
    comment_payload['created_by_id'] = created_by_id
    return await board_row_repository.create_board_row_comment(
        comment_payload,
        session=session,
    )


async def get_board_row_comment_by_id(
    comment_id: UUID, session: AsyncSession
) -> BoardRowComment:
    """
    Retrieve a single board row comment by its identifier.

    :param comment_id: The UUID of the comment to retrieve.
    :param session: The active database session.
    :return: The matching comment model.
    """
    return await board_row_repository.get_board_row_comment_by_id(
        comment_id=comment_id,
        session=session,
    )


async def get_board_row_comments_by_board_row_id(
    board_row_id: UUID, session: AsyncSession
) -> list[BoardRowComment]:
    """
    Retrieve all comments linked to a board row.

    :param board_row_id: The UUID of the parent board row.
    :param session: The active database session.
    :return: A list of matching comment models.
    """
    return await board_row_repository.get_board_row_comments_by_board_row_id(
        board_row_id=board_row_id,
        session=session,
    )


async def update_board_row_comment(
    comment_id: UUID,
    comment_data: BoardRowCommentUpdateDTO,
    session: AsyncSession,
) -> BoardRowComment:
    """
    Update a board row comment.

    :param comment_id: The UUID of the comment to update.
    :param comment_data: The validated payload containing updated comment values.
    :param session: The active database session.
    :return: The updated comment model.
    """
    return await board_row_repository.update_board_row_comment(
        comment_id=comment_id,
        updated_data=comment_data.model_dump(exclude_none=True),
        session=session,
    )


async def delete_board_row_comment(comment_id: UUID, session: AsyncSession) -> None:
    """
    Delete a board row comment.

    :param comment_id: The UUID of the comment to delete.
    :param session: The active database session.
    :return: None.
    """
    await board_row_repository.delete_board_row_comment(
        comment_id=comment_id,
        session=session,
    )
