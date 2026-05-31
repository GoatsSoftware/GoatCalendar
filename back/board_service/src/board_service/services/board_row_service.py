from uuid import UUID

from shared_models.schemas import BoardRow
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_row_repository


async def get_board_row_by_id(board_row_id: UUID, session=AsyncSession) -> BoardRow:
    return await board_row_repository.get_board_row_by_id(
        board_row_id=board_row_id,
        session=session,
    )


async def get_board_rows_by_board_id(
    board_id: UUID,
    session=AsyncSession,
) -> list[BoardRow]:
    return await board_row_repository.get_board_rows_by_board_id(
        board_id=board_id,
        session=session,
    )
