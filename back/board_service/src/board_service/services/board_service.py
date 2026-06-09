from uuid import UUID

from shared_models.dtos.board_in_dtos import BoardCreateDTO, BoardUpdateDTO
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.user_dtos import UserWithBoardPermissionOutDTO
from shared_models.schemas.board import Board
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_repository


def serialize_board_as_dto(board: Board) -> BoardOutDTO:
    """
    Convert a complex relational Board database entity into a clean output DTO.

    Flattens indirect user permissions into standard user profile transfer models.

    :param board: The source Board entity record from the database.
    :return: A completely initialized and validated BoardOutDTO instance.
    """
    board_dto = BoardOutDTO.model_validate(board, from_attributes=True)

    # store users invited in this board as new objects
    for user_relation in board.user_relations:
        board_dto.users.append(
            UserWithBoardPermissionOutDTO.model_validate(
                {
                    **user_relation.user.model_dump(),
                    "user_role_in_board": user_relation.user_role_in_board,
                },
            ),
        )

    return board_dto


async def get_all_boards(session: AsyncSession) -> list[BoardOutDTO]:
    """
    Retrieve and serialize all boards available in the system.

    :param session: The active database session.
    :return: A list of structured board output DTOs.
    """
    return [
        serialize_board_as_dto(board=board)
        for board in await board_repository.get_all_boards(session=session)
    ]


async def get_board_by_id(board_id: UUID, session: AsyncSession) -> BoardOutDTO:
    """
    Retrieve a specific board entity and return its structural DTO layout.

    :param board_id: The UUID identifier of the board.
    :param session: The active database session.
    :return: The structured board output DTO.
    """
    return serialize_board_as_dto(
        board=await board_repository.get_board_by_id(
            board_id=board_id,
            session=session,
        ),
    )


async def get_user_boards(user_id: UUID, session: AsyncSession) -> list[BoardOutDTO]:
    """
    Retrieve and serialize all boards created by a single user identifier.

    :param user_id: The UUID identifier of the author user.
    :param session: The active database session.
    :return: A list of structured board output DTOs.
    """
    return [
        serialize_board_as_dto(board=board)
        for board in await board_repository.get_user_boards(
            user_id=user_id,
            session=session,
        )
    ]


async def create_board(board_data: BoardCreateDTO, session: AsyncSession) -> BoardOutDTO:
    """Create a new board and return its serialized DTO."""
    board = await board_repository.create_board(
        board_data.model_dump(exclude_none=True),
        session=session,
    )
    return serialize_board_as_dto(board=board)


async def update_board(
    board_id: UUID,
    board_data: BoardUpdateDTO,
    session: AsyncSession,
) -> BoardOutDTO:
    """Update an existing board and return the latest DTO."""
    board = await board_repository.update_board(
        board_id=board_id,
        updated_data=board_data.model_dump(exclude_none=True),
        session=session,
    )
    return serialize_board_as_dto(board=board)


async def delete_board(board_id: UUID, session: AsyncSession) -> None:
    """Delete a board by its identifier."""
    await board_repository.delete_board(board_id=board_id, session=session)
