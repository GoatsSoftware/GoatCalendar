from uuid import UUID

from shared_models.schemas import Board, UserBoardPermission
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
        joinedload(Board.columns),
        joinedload(Board.user_relations).joinedload(UserBoardPermission.user),
        joinedload(Board.events),
    )


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
