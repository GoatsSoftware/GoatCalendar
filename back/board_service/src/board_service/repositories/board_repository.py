from uuid import UUID

from shared_models.schemas import Board, BoardColumn, BoardEvent, UserBoardPermission
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlalchemy import delete


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
    return (joinedload(BoardColumn.created_by),)


def get_board_event_dependencies_loading_options() -> tuple:
    return (joinedload(BoardEvent.created_by),)


def get_board_permission_dependencies_loading_options() -> tuple:
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


async def create_board(board_data: dict, session: AsyncSession) -> Board:
    """Create a new board record in the database."""
    board = Board(**board_data)
    session.add(board)
    await session.commit()
    await session.refresh(board)
    return board


async def update_board(board_id: UUID, updated_data: dict, session: AsyncSession) -> Board:
    """Update an existing board record."""
    board = await session.get(Board, board_id)
    if board is None:
        raise NoResultFound
    for key, value in updated_data.items():
        setattr(board, key, value)
    session.add(board)
    await session.commit()
    await session.refresh(board)
    return board


async def delete_board(board_id: UUID, session: AsyncSession) -> Board:
    """Delete an existing board record."""
    board = await session.get(Board, board_id)
    if board is None:
        raise NoResultFound
    await session.delete(board)
    await session.commit()
    return board


async def create_board_column(column_data: dict, session: AsyncSession) -> BoardColumn:
    """Create a new board column."""
    column = BoardColumn(**column_data)
    session.add(column)
    await session.commit()
    await session.refresh(column)
    return column


async def get_board_column_by_id(column_id: UUID, session: AsyncSession) -> BoardColumn:
    statement = (
        select(BoardColumn)
        .where(BoardColumn.id == column_id)
        .options(*get_board_column_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_columns_by_board_id(
    board_id: UUID, session: AsyncSession
) -> list[BoardColumn]:
    statement = (
        select(BoardColumn)
        .where(BoardColumn.board_id == board_id)
        .options(*get_board_column_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_column(column_id: UUID, updated_data: dict, session: AsyncSession) -> BoardColumn:
    """Update a board column."""
    column = await session.get(BoardColumn, column_id)
    if column is None:
        raise NoResultFound
    for key, value in updated_data.items():
        setattr(column, key, value)
    session.add(column)
    await session.commit()
    await session.refresh(column)
    return column


async def delete_board_column(column_id: UUID, session: AsyncSession) -> None:
    """Delete a board column."""
    stmt = delete(BoardColumn).where(BoardColumn.id == column_id)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        raise NoResultFound
    await session.commit()


async def create_board_event(event_data: dict, session: AsyncSession) -> BoardEvent:
    """Create a board event/milestone."""
    event = BoardEvent(**event_data)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def get_board_event_by_id(event_id: UUID, session: AsyncSession) -> BoardEvent:
    statement = (
        select(BoardEvent)
        .where(BoardEvent.id == event_id)
        .options(*get_board_event_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().one()


async def get_board_events_by_board_id(
    board_id: UUID, session: AsyncSession
) -> list[BoardEvent]:
    statement = (
        select(BoardEvent)
        .where(BoardEvent.board_id == board_id)
        .options(*get_board_event_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_board_event(event_id: UUID, updated_data: dict, session: AsyncSession) -> BoardEvent:
    """Update a board event."""
    event = await session.get(BoardEvent, event_id)
    if event is None:
        raise NoResultFound
    for key, value in updated_data.items():
        setattr(event, key, value)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def delete_board_event(event_id: UUID, session: AsyncSession) -> None:
    """Delete a board event."""
    stmt = delete(BoardEvent).where(BoardEvent.id == event_id)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        raise NoResultFound
    await session.commit()


async def add_user_to_board(permission_data: dict, session: AsyncSession) -> UserBoardPermission:
    """Add a user to a board with specified role."""
    permission = UserBoardPermission(**permission_data)
    session.add(permission)
    await session.commit()
    await session.refresh(permission)
    return permission


async def get_board_permission(
    board_id: UUID, user_id: UUID, session: AsyncSession
) -> UserBoardPermission:
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
    board_id: UUID, session: AsyncSession
) -> list[UserBoardPermission]:
    statement = (
        select(UserBoardPermission)
        .where(UserBoardPermission.board_id == board_id)
        .options(*get_board_permission_dependencies_loading_options())
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_user_board_permission(
    board_id: UUID, user_id: UUID, updated_data: dict, session: AsyncSession
) -> UserBoardPermission:
    """Update user's role in a board."""
    stmt = select(UserBoardPermission).where(
        UserBoardPermission.board_id == board_id,
        UserBoardPermission.user_id == user_id,
    )
    result = await session.exec(stmt)
    permission = result.first()
    if permission is None:
        raise NoResultFound
    for key, value in updated_data.items():
        setattr(permission, key, value)
    session.add(permission)
    await session.commit()
    await session.refresh(permission)
    return permission


async def remove_user_from_board(board_id: UUID, user_id: UUID, session: AsyncSession) -> None:
    """Remove user from board."""
    stmt = delete(UserBoardPermission).where(
        UserBoardPermission.board_id == board_id,
        UserBoardPermission.user_id == user_id,
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        raise NoResultFound
    await session.commit()
