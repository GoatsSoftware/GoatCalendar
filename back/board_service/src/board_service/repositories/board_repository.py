from uuid import UUID

from shared_models.schemas import Board, UserBoardPermission
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select


def get_board_dependencies_loading_options() -> tuple:
    return (
        joinedload(Board.created_by),
        joinedload(Board.columns),
        joinedload(Board.user_relations).joinedload(UserBoardPermission.user),
        joinedload(Board.events),
    )


async def get_all_boards(session=AsyncSession) -> list[Board]:
    statement = select(Board).options(*get_board_dependencies_loading_options())

    result = await session.exec(statement)
    return result.unique().all()


async def get_board_by_id(board_id: UUID, session=AsyncSession) -> Board:
    statement = (
        select(Board)
        .options(*get_board_dependencies_loading_options())
        .where(Board.id == board_id)
    )

    result = await session.exec(statement)
    return result.unique().one()


async def get_user_boards(user_id: UUID, session=AsyncSession) -> list[Board]:
    statement = (
        select(Board)
        .options(*get_board_dependencies_loading_options())
        .where(Board.created_by_id == user_id)
    )

    result = await session.exec(statement)
    return result.unique().all()
