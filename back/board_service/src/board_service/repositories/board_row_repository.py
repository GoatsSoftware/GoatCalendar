from uuid import UUID

from shared_models.schemas import BoardRow, BoardRowComment, BoardRowTask
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select


def get_board_row_dependencies_loading_options() -> tuple:
    return (
        joinedload(BoardRow.tasks).options(
            joinedload(BoardRowTask.board_column),
            joinedload(BoardRowTask.assigned_to),
            joinedload(BoardRowTask.created_by),
        ),
        joinedload(BoardRow.comments).joinedload(BoardRowComment.created_by),
        joinedload(BoardRow.created_by),
    )


async def get_board_row_by_id(board_row_id: UUID, session=AsyncSession) -> BoardRow:
    statement = (
        select(BoardRow)
        .where(BoardRow.id == board_row_id)
        .options(*get_board_row_dependencies_loading_options())
    )

    result = await session.exec(statement)
    return result.unique().one()


async def get_board_rows_by_board_id(
    board_id: UUID,
    session=AsyncSession,
) -> list[BoardRow]:
    statement = (
        select(BoardRow)
        .where(BoardRow.board_id == board_id)
        .options(*get_board_row_dependencies_loading_options())
    )

    result = await session.exec(statement)
    return result.unique().all()
