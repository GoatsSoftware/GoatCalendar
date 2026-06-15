from uuid import UUID

from shared_models.dtos import (
    BoardColumnCreateDTO,
    BoardColumnUpdateDTO,
    BoardCreateDTO,
    BoardEventCreateDTO,
    BoardEventUpdateDTO,
    BoardPermissionCreateDTO,
    BoardPermissionUpdateDTO,
    BoardUpdateDTO,
)
from shared_models.enums import UserRoleInBoard
from shared_models.schemas import Board, BoardColumn, BoardEvent, UserBoardPermission
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select


def get_board_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a Board query to avoid N+1 issues.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (
        joinedload(Board.created_by),
        joinedload(Board.columns).joinedload(BoardColumn.created_by),
        joinedload(Board.user_relations).joinedload(UserBoardPermission.user),
        joinedload(Board.events).joinedload(BoardEvent.created_by),
    )


def get_board_column_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardColumn query.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (joinedload(BoardColumn.created_by),)


def get_board_event_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a BoardEvent query.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (joinedload(BoardEvent.created_by),)


def get_board_permission_dependencies_loading_options() -> tuple:
    """
    Define eager loading relationships for a UserBoardPermission query.

    :return: A tuple of SQLAlchemy loading options.
    """
    return (joinedload(UserBoardPermission.user),)


async def get_all_boards(session: AsyncSession) -> list[Board]:
    """
    Fetch all boards from the database with their nested relationships loaded.

    :param session: The active database session.
    :return: A list of all Board records.
    """
    statement = select(Board).options(*get_board_dependencies_loading_options())

    result = await session.exec(statement)
    return result.unique().all()


async def get_board_by_id(board_id: UUID, session: AsyncSession) -> Board:
    """
    Fetch a single board by its unique identifier.

    :param board_id: The UUID of the board to retrieve.
    :param session: The active database session.
    :return: The matching Board record.
    """
    statement = (
        select(Board)
        .options(*get_board_dependencies_loading_options())
        .where(Board.id == board_id)
    )

    result = await session.exec(statement)
    return result.unique().one()


async def get_user_boards(user_id: UUID, session: AsyncSession) -> list[Board]:
    """
    Fetch all boards created by a specific user.

    :param user_id: The UUID of the user creator.
    :param session: The active database session.
    :return: A list of Board records created by the user.
    """
    statement = (
        select(Board)
        .options(*get_board_dependencies_loading_options())
        .where(Board.created_by_id == user_id)
    )

    result = await session.exec(statement)
    return result.unique().all()


async def create_board(
    board_data: BoardCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> Board:
    """
    Create a new board record in the database.

    :param board_data: The raw board payload ready for persistence.
    :param created_by_id: The UUID of the user creating the board.
    :param session: The active database session.
    :return: The newly created board model.
    """
    user_permission = UserBoardPermission()
    board = Board()
    board.name = board_data.name
    board.description = board_data.description
    board.created_by_id = created_by_id
    user_permission.user_id = created_by_id
    user_permission.user_role_in_board = UserRoleInBoard.OWNER

    board.user_relations.append(user_permission)

    session.add(board)
    await session.commit()
    await session.refresh(board)

    return await get_board_by_id(board_id=board.id, session=session)


async def update_board(
    board_id: UUID,
    updated_data: BoardUpdateDTO,
    session: AsyncSession,
) -> Board:
    """
    Update an existing board record.

    :param board_id: The UUID of the board to update.
    :param updated_data: The raw attributes to apply on the board.
    :param session: The active database session.
    :return: The updated board model.
    :raises NoResultFound: If the board does not exist.
    """
    board = await session.get(Board, board_id)
    if board is None:
        raise NoResultFound

    board.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    session.add(board)
    await session.commit()

    return await get_board_by_id(board_id=board_id, session=session)


async def delete_board(board_id: UUID, session: AsyncSession) -> None:
    """
    Delete an existing board record.

    :param board_id: The UUID of the board to delete.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the board does not exist.
    """
    board = await session.get(Board, board_id)
    if board is None:
        raise NoResultFound

    await session.delete(board)
    await session.commit()


async def create_board_column(
    column_data: BoardColumnCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardColumn:
    """
    Create a new board column.

    :param column_data: The raw board column payload ready for persistence.
    :param created_by_id: The UUID of the user creating the column.
    :param session: The active database session.
    :return: The newly created board column model.
    """
    additional_data = {"created_by_id": created_by_id}

    column = BoardColumn()
    column.sqlmodel_update(
        obj=column_data.model_dump(exclude_unset=True),
        update=additional_data,
    )

    session.add(column)
    await session.commit()
    await session.refresh(column)

    return await get_board_column_by_id(
        column_id=column.id,
        session=session,
    )


async def get_board_column_by_id(column_id: UUID, session: AsyncSession) -> BoardColumn:
    """
    Fetch a single board column by its unique identifier.

    :param column_id: The UUID of the column to retrieve.
    :param session: The active database session.
    :return: The matching board column record.
    """
    statement = (
        select(BoardColumn)
        .where(BoardColumn.id == column_id)
        .options(*get_board_column_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_columns_by_board_id(
    board_id: UUID,
    session: AsyncSession,
) -> list[BoardColumn]:
    """
    Fetch all columns associated with a specific board.

    :param board_id: The UUID of the parent board.
    :param session: The active database session.
    :return: A list of matching board column records.
    """
    statement = (
        select(BoardColumn)
        .where(BoardColumn.board_id == board_id)
        .options(*get_board_column_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_column(
    column_id: UUID,
    updated_data: BoardColumnUpdateDTO,
    session: AsyncSession,
) -> BoardColumn:
    """
    Update a board column.

    :param column_id: The UUID of the column to update.
    :param updated_data: The raw attributes to apply on the column.
    :param session: The active database session.
    :return: The updated board column model.
    :raises NoResultFound: If the column does not exist.
    """
    column = await session.get(BoardColumn, column_id)

    if column is None:
        raise NoResultFound

    column.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    await session.commit()

    return await get_board_column_by_id(
        column_id=column.id,
        session=session,
    )


async def delete_board_column(column_id: UUID, session: AsyncSession) -> None:
    """
    Delete a board column.

    :param column_id: The UUID of the column to delete.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the column does not exist.
    """
    stmt = delete(BoardColumn).where(BoardColumn.id == column_id)
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise NoResultFound

    await session.commit()


async def create_board_event(
    event_data: BoardEventCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardEvent:
    """
    Create a board event or milestone.

    :param event_data: The raw board event payload ready for persistence.
    :param created_by_id: The UUID of the user creating the event.
    :param session: The active database session.
    :return: The newly created board event model.
    """
    additional_data = {
        "created_by_id": created_by_id,
        "version": 1,
    }

    event = BoardEvent()
    event.sqlmodel_update(
        obj=event_data.model_dump(exclude_unset=True),
        update=additional_data,
    )
    session.add(event)

    await session.commit()
    await session.refresh(event)

    return await get_board_event_by_id(
        event_id=event.id,
        session=session,
    )


async def get_board_event_by_id(event_id: UUID, session: AsyncSession) -> BoardEvent:
    """
    Fetch a single board event by its unique identifier.

    :param event_id: The UUID of the event to retrieve.
    :param session: The active database session.
    :return: The matching board event record.
    """
    statement = (
        select(BoardEvent)
        .where(BoardEvent.id == event_id)
        .options(*get_board_event_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_events_by_board_id(
    board_id: UUID,
    session: AsyncSession,
) -> list[BoardEvent]:
    """
    Fetch all events associated with a specific board.

    :param board_id: The UUID of the parent board.
    :param session: The active database session.
    :return: A list of matching board event records.
    """
    statement = (
        select(BoardEvent)
        .where(BoardEvent.board_id == board_id)
        .options(*get_board_event_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_event(
    event_id: UUID,
    updated_data: BoardEventUpdateDTO,
    session: AsyncSession,
) -> BoardEvent:
    """
    Update a board event.

    :param event_id: The UUID of the event to update.
    :param updated_data: The raw attributes to apply on the event.
    :param session: The active database session.
    :return: The updated board event model.
    :raises NoResultFound: If the event does not exist.
    """
    event = await session.get(BoardEvent, event_id)

    if event is None:
        raise NoResultFound

    event.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    await session.commit()

    return await get_board_event_by_id(
        event_id=event.id,
        session=session,
    )


async def delete_board_event(event_id: UUID, session: AsyncSession) -> None:
    """
    Delete a board event.

    :param event_id: The UUID of the event to delete.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the event does not exist.
    """
    stmt = delete(BoardEvent).where(BoardEvent.id == event_id)
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise NoResultFound

    await session.commit()


async def add_user_to_board(
    permission_data: BoardPermissionCreateDTO,
    session: AsyncSession,
) -> UserBoardPermission:
    """
    Add a user to a board with a specific role.

    :param permission_data: The raw permission payload ready for persistence.
    :param session: The active database session.
    :return: The newly created board permission model.
    """
    permission = UserBoardPermission()
    permission.sqlmodel_update(obj=permission_data.model_dump(exclude_unset=True))
    session.add(permission)

    await session.commit()
    await session.refresh(permission)

    return await get_board_permission(
        board_id=permission.board_id,
        user_id=permission.user_id,
        session=session,
    )


async def get_board_permission(
    board_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> UserBoardPermission:
    """
    Fetch a single permission attached to a board and user pair.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param session: The active database session.
    :return: The matching board permission record.
    """
    statement = (
        select(UserBoardPermission)
        .where(
            UserBoardPermission.board_id == board_id,
            UserBoardPermission.user_id == user_id,
        )
        .options(*get_board_permission_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_permissions_by_board_id(
    board_id: UUID,
    session: AsyncSession,
) -> list[UserBoardPermission]:
    """
    Fetch all permissions attached to a specific board.

    :param board_id: The UUID of the target board.
    :param session: The active database session.
    :return: A list of matching board permission records.
    """
    statement = (
        select(UserBoardPermission)
        .where(UserBoardPermission.board_id == board_id)
        .options(*get_board_permission_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_user_board_permission(
    board_id: UUID,
    user_id: UUID,
    updated_data: BoardPermissionUpdateDTO,
    session: AsyncSession,
) -> UserBoardPermission:
    """
    Update a user's role in a board.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param updated_data: The raw attributes to apply on the permission.
    :param session: The active database session.
    :return: The updated board permission model.
    :raises NoResultFound: If the permission does not exist.
    """
    stmt = select(UserBoardPermission).where(
        UserBoardPermission.board_id == board_id,
        UserBoardPermission.user_id == user_id,
    )
    result = await session.exec(stmt)
    permission = result.first()

    if permission is None:
        raise NoResultFound

    permission.sqlmodel_update(obj=updated_data.model_dump(exclude_unset=True))

    await session.commit()

    return await get_board_permission(
        board_id=permission.board_id,
        user_id=permission.user_id,
        session=session,
    )


async def remove_user_from_board(
    board_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """
    Remove a user from a board.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param session: The active database session.
    :return: None.
    :raises NoResultFound: If the permission does not exist.
    """
    stmt = delete(UserBoardPermission).where(
        UserBoardPermission.board_id == board_id,
        UserBoardPermission.user_id == user_id,
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise NoResultFound

    await session.commit()
