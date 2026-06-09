from uuid import UUID

from shared_models.schemas import BoardRow, BoardRowComment, BoardRowTask
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlalchemy import update, delete


def get_board_row_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardRow query to avoid N+1 issues.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (
        joinedload(BoardRow.tasks).options(
            joinedload(BoardRowTask.board_column),
            joinedload(BoardRowTask.assigned_to),
            joinedload(BoardRowTask.created_by),
        ),
        joinedload(BoardRow.comments).joinedload(BoardRowComment.created_by),
        joinedload(BoardRow.created_by),
    )


async def get_board_row_by_id(board_row_id: UUID, session: AsyncSession) -> BoardRow:
    """
    Fetch a single board row by its unique identifier.

    :param board_row_id: The UUID of the row to retrieve.
    :param session: The active database session.
    :return: The matching BoardRow record.
    """
    statement = (
        select(BoardRow)
        .where(BoardRow.id == board_row_id)
        .options(*get_board_row_dependencies_loading_options())
    )

    result = await session.exec(statement)
    return result.unique().one()


async def get_board_rows_by_board_id(
    board_id: UUID,
    session: AsyncSession,
) -> list[BoardRow]:
    """
    Fetch all horizontal rows associated with a specific board.

    :param board_id: The UUID of the board.
    :param session: The active database session.
    :return: A list of matching BoardRow records.
    """
    statement = (
        select(BoardRow)
        .where(BoardRow.board_id == board_id)
        .options(*get_board_row_dependencies_loading_options())
    )

    result = await session.exec(statement)
    return result.unique().all()


async def create_board_row_task(task_data: dict, session: AsyncSession) -> BoardRowTask:
    """Create a new task inside a board row."""
    task = BoardRowTask(**task_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_board_row_task_with_version(
    task_id: UUID, updated_data: dict, version_from_client: int, session: AsyncSession
) -> BoardRowTask | None:
    """Attempt to update a task only if the version matches (optimistic locking).

    Returns the updated task, or None if the version didn't match / no row was updated.
    """
    stmt = (
        update(BoardRowTask)
        .where(BoardRowTask.id == task_id)
        .where(BoardRowTask.version == version_from_client)
        .values({**updated_data, "version": BoardRowTask.version + 1})
    )

    result = await session.execute(stmt)

    # result.rowcount is available for DML operations
    if result.rowcount == 0:
        return None

    await session.commit()
    return await session.get(BoardRowTask, task_id)


async def delete_board_row_task(task_id: UUID, session: AsyncSession) -> None:
    """Delete a task by id."""
    stmt = delete(BoardRowTask).where(BoardRowTask.id == task_id)
    await session.execute(stmt)
    await session.commit()


async def create_board_row(board_row_data: dict, session: AsyncSession) -> BoardRow:
    """Create a new board row record in the database."""
    board_row = BoardRow(**board_row_data)
    session.add(board_row)
    await session.commit()
    await session.refresh(board_row)
    return board_row


async def update_board_row(board_row_id: UUID, updated_data: dict, session: AsyncSession) -> BoardRow:
    """Update an existing board row record."""
    board_row = await session.get(BoardRow, board_row_id)
    if board_row is None:
        raise NoResultFound
    for key, value in updated_data.items():
        setattr(board_row, key, value)
    session.add(board_row)
    await session.commit()
    await session.refresh(board_row)
    return board_row


async def delete_board_row(board_row_id: UUID, session: AsyncSession) -> BoardRow:
    """Delete an existing board row record."""
    board_row = await session.get(BoardRow, board_row_id)
    if board_row is None:
        raise NoResultFound
    await session.delete(board_row)
    await session.commit()
    return board_row
