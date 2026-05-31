from uuid import UUID

from shared_models.schemas.board import Board
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_repository


async def get_all_boards(session=AsyncSession) -> list[Board]:
    return await board_repository.get_all_boards(session=session)


async def get_board_by_id(board_id: UUID, session=AsyncSession) -> Board:
    return await board_repository.get_board_by_id(board_id=board_id, session=session)


async def get_user_boards(user_id: UUID, session=AsyncSession) -> list[Board]:
    return await board_repository.get_user_boards(user_id=user_id, session=session)
