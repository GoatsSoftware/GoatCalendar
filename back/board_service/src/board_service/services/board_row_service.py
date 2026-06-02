from uuid import UUID

from shared_models.schemas import BoardRow
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_row_repository


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
