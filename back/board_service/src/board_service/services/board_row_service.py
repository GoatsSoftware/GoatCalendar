from uuid import UUID

from shared_models.dtos.board_row_in_dtos import BoardRowCreateDTO, BoardRowUpdateDTO
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


async def create_board_row(
    board_row_data: BoardRowCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardRow:
    """Create a new row inside a board."""
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
    """Update a board row's properties."""
    return await board_row_repository.update_board_row(
        board_row_id=board_row_id,
        updated_data=board_row_data.model_dump(exclude_none=True),
        session=session,
    )


async def delete_board_row(board_row_id: UUID, session: AsyncSession) -> None:
    """Delete a board row by its identifier."""
    await board_row_repository.delete_board_row(
        board_row_id=board_row_id,
        session=session,
    )
