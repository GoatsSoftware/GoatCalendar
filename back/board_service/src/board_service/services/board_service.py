from uuid import UUID

from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.user_dtos import UserWithBoardPermissionOutDTO
from shared_models.schemas.board import Board
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.repositories import board_repository


def serialize_board_as_dto(board: Board) -> BoardOutDTO:
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

    print(board)

    return board_dto


async def get_all_boards(session=AsyncSession) -> list[BoardOutDTO]:
    return list(
        serialize_board_as_dto(board=board)
        for board in await board_repository.get_all_boards(session=session)
    )


async def get_board_by_id(board_id: UUID, session=AsyncSession) -> BoardOutDTO:
    return serialize_board_as_dto(
        board=await board_repository.get_board_by_id(
            board_id=board_id,
            session=session,
        ),
    )


async def get_user_boards(user_id: UUID, session=AsyncSession) -> list[BoardOutDTO]:
    return list(
        serialize_board_as_dto(board=board)
        for board in await board_repository.get_user_boards(
            user_id=user_id,
            session=session,
        )
    )
