from uuid import UUID

from shared_models.dtos import (
    BoardRowCommentCreateDTO,
    BoardRowCommentUpdateDTO,
    BoardRowCreateDTO,
    BoardRowTaskCreateDTO,
    BoardRowTaskUpdateDTO,
    BoardRowUpdateDTO,
)
from shared_models.schemas import BoardColumn, BoardRow, BoardRowComment, BoardRowTask
from sqlalchemy import delete, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select


def get_board_row_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardRow query to avoid N+1 issues.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (
        joinedload(BoardRow.tasks).options(
            joinedload(BoardRowTask.board_column).joinedload(BoardColumn.created_by),
            joinedload(BoardRowTask.assigned_to),
            joinedload(BoardRowTask.created_by),
        ),
        joinedload(BoardRow.comments).joinedload(BoardRowComment.created_by),
        joinedload(BoardRow.created_by),
    )


def get_board_row_task_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardRowTask query.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (
        joinedload(BoardRowTask.board_column).joinedload(BoardColumn.created_by),
        joinedload(BoardRowTask.assigned_to),
        joinedload(BoardRowTask.created_by),
    )


def get_board_row_comment_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardRowComment query.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (joinedload(BoardRowComment.created_by),)


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


async def create_board_row_task(
    task_data: BoardRowTaskCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRowTask:
    """
    Create a new task inside a board row.

    :param task_data: The raw task payload ready for persistence.
    :param created_by_id: The UUID of the user creating the task.
    :param session: The active database session.
    :return: The newly created board row task model.
    """
    additional_data = {
        "created_by_id": created_by_id,
        "version": 1,
    }

    task = BoardRowTask()
    task.sqlmodel_update(
        obj=task_data.model_dump(exclude_unset=True),
        update=additional_data,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return await get_board_row_task_by_id(
        task_id=task.id,
        session=session,
    )


async def get_board_row_task_by_id(
    task_id: UUID,
    session: AsyncSession,
) -> BoardRowTask:
    """
    Fetch a single board row task by its unique identifier.

    :param task_id: The UUID of the task to retrieve.
    :param session: The active database session.
    :return: The matching board row task record.
    """
    statement = (
        select(BoardRowTask)
        .where(BoardRowTask.id == task_id)
        .options(*get_board_row_task_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_row_tasks_by_board_row_id(
    board_row_id: UUID,
    session: AsyncSession,
) -> list[BoardRowTask]:
    """
    Fetch all tasks associated with a specific board row.

    :param board_row_id: The UUID of the parent board row.
    :param session: The active database session.
    :return: A list of matching board row task records.
    """
    statement = (
        select(BoardRowTask)
        .where(BoardRowTask.board_row_id == board_row_id)
        .options(*get_board_row_task_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def get_board_row_tasks_by_board_column_id(
    board_column_id: UUID,
    session: AsyncSession,
) -> list[BoardRowTask]:
    """
    Fetch all tasks associated with a specific board column.

    :param board_column_id: The UUID of the parent board column.
    :param session: The active database session.
    :return: A list of matching board row task records.
    """
    statement = (
        select(BoardRowTask)
        .where(BoardRowTask.board_column_id == board_column_id)
        .options(*get_board_row_task_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_row_task_with_version(
    task_id: UUID,
    updated_data: BoardRowTaskUpdateDTO,
    version_from_client: int,
    session: AsyncSession,
) -> BoardRowTask | None:
    """
    Attempt to update a task only if the version matches.

    :param task_id: The UUID of the task to update.
    :param updated_data: The raw attributes to apply on the task.
    :param version_from_client: The optimistic locking version provided by the client.
    :param session: The active database session.
    :return: The updated task model, or None if no row was updated.
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
    return await get_board_row_task_by_id(task_id=task_id, session=session)


async def delete_board_row_task(task_id: UUID, session: AsyncSession) -> None:
    """
    Delete a task by its identifier.

    :param task_id: The UUID of the task to delete.
    :param session: The active database session.
    :return: None.
    """
    stmt = delete(BoardRowTask).where(BoardRowTask.id == task_id)
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise NoResultFound

    await session.commit()


async def create_board_row(
    board_row_data: BoardRowCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRow:
    """
    Create a new board row record in the database.

    :param board_row_data: The raw board row payload ready for persistence.
    :param created_by_id: The UUID of the user creating the board row.
    :param session: The active database session.
    :return: The newly created board row model.
    """
    additional_data = {"created_by_id": created_by_id}

    board_row = BoardRow()
    board_row.sqlmodel_update(
        obj=board_row_data.model_dump(exclude_unset=True),
        update=additional_data,
    )

    session.add(board_row)
    await session.commit()
    await session.refresh(board_row)

    return await get_board_row_by_id(
        board_row_id=board_row.id,
        session=session,
    )


async def update_board_row(
    board_row_id: UUID,
    updated_data: BoardRowUpdateDTO,
    session: AsyncSession,
) -> BoardRow:
    """
    Update an existing board row record.

    :param board_row_id: The UUID of the row to update.
    :param updated_data: The raw attributes to apply on the row.
    :param session: The active database session.
    :return: The updated board row model.
    :raises NoResultFound: If the row does not exist.
    """
    board_row = await session.get(BoardRow, board_row_id)

    if board_row is None:
        raise NoResultFound

    board_row.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    session.add(board_row)
    await session.commit()
    await session.refresh(board_row)

    return await get_board_row_by_id(
        board_row_id=board_row_id,
        session=session,
    )


async def delete_board_row(board_row_id: UUID, session: AsyncSession) -> None:
    """
    Delete an existing board row record.

    :param board_row_id: The UUID of the row to delete.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the row does not exist.
    """
    board_row = await session.get(BoardRow, board_row_id)

    if board_row is None:
        raise NoResultFound

    await session.delete(board_row)
    await session.commit()


async def create_board_row_comment(
    comment_data: BoardRowCommentCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRowComment:
    """
    Create a new comment on a board row.

    :param comment_data: The raw comment payload ready for persistence.
    :param created_by_id: The UUID of the user creating the comment.
    :param session: The active database session.
    :return: The newly created board row comment model.
    """
    additional_data = {"created_by_id": created_by_id}

    comment = BoardRowComment()
    comment.sqlmodel_update(
        obj=comment_data.model_dump(exclude_unset=False),
        update=additional_data,
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return await get_board_row_comment_by_id(
        comment_id=comment.id,
        session=session,
    )


async def get_board_row_comment_by_id(
    comment_id: UUID,
    session: AsyncSession,
) -> BoardRowComment:
    """
    Fetch a single board row comment by its unique identifier.

    :param comment_id: The UUID of the comment to retrieve.
    :param session: The active database session.
    :return: The matching board row comment record.
    """
    statement = (
        select(BoardRowComment)
        .where(BoardRowComment.id == comment_id)
        .options(*get_board_row_comment_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_row_comments_by_board_row_id(
    board_row_id: UUID,
    session: AsyncSession,
) -> list[BoardRowComment]:
    """
    Fetch all comments associated with a specific board row.

    :param board_row_id: The UUID of the parent board row.
    :param session: The active database session.
    :return: A list of matching board row comment records.
    """
    statement = (
        select(BoardRowComment)
        .where(BoardRowComment.board_row_id == board_row_id)
        .options(*get_board_row_comment_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_row_comment(
    comment_id: UUID,
    updated_data: BoardRowCommentUpdateDTO,
    session: AsyncSession,
) -> BoardRowComment:
    """
    Update a board row comment.

    :param comment_id: The UUID of the comment to update.
    :param updated_data: The raw attributes to apply on the comment.
    :param session: The active database session.
    :return: The updated board row comment model.
    :raises NoResultFound: If the comment does not exist.
    """
    comment = await session.get(BoardRowComment, comment_id)

    if comment is None:
        raise NoResultFound

    comment.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return await get_board_row_comment_by_id(
        comment_id=comment_id,
        session=session,
    )


async def delete_board_row_comment(comment_id: UUID, session: AsyncSession) -> None:
    """
    Delete a board row comment.

    :param comment_id: The UUID of the comment to delete.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the comment does not exist.
    """
    stmt = delete(BoardRowComment).where(BoardRowComment.id == comment_id)
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise NoResultFound

    await session.commit()
