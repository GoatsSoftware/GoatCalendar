from uuid import UUID

from shared_models.dtos.board_event_out_dto import BoardEventOutDTO
from shared_models.dtos.board_permission_out_dto import BoardPermissionOutDTO
from shared_models.dtos.board_in_dtos import BoardCreateDTO, BoardUpdateDTO
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.user_dtos import UserWithBoardPermissionOutDTO
from shared_models.schemas import Board, BoardColumn, BoardEvent, UserBoardPermission
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


def serialize_board_event_as_dto(event: BoardEvent) -> BoardEventOutDTO:
    return BoardEventOutDTO.model_validate(event, from_attributes=True)


def serialize_board_permission_as_dto(
    permission: UserBoardPermission,
) -> BoardPermissionOutDTO:
    return BoardPermissionOutDTO.model_validate(permission, from_attributes=True)


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


async def create_board(
    board_data: BoardCreateDTO,
    created_by_id: UUID,
    session: AsyncSession,
) -> BoardOutDTO:
    """Create a new board and return its serialized DTO."""
    board_payload = board_data.model_dump(exclude_none=True)
    board_payload["created_by_id"] = created_by_id
    board = await board_repository.create_board(
        board_payload,
        session=session,
    )
    return serialize_board_as_dto(board=board)


async def get_board_column_by_id(column_id: UUID, session: AsyncSession) -> BoardColumn:
    return await board_repository.get_board_column_by_id(column_id=column_id, session=session)


async def get_board_columns_by_board_id(
    board_id: UUID, session: AsyncSession
) -> list[BoardColumn]:
    return await board_repository.get_board_columns_by_board_id(
        board_id=board_id,
        session=session,
    )


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


# Column service methods

async def create_board_column(column_data, created_by_id: UUID, session: AsyncSession):
    """Create a new board column."""
    from shared_models.dtos.board_column_in_dto import BoardColumnCreateDTO
    column_payload = column_data.model_dump(exclude_none=True)
    column_payload['created_by_id'] = created_by_id
    return await board_repository.create_board_column(
        column_payload,
        session=session,
    )


async def update_board_column(column_id: UUID, column_data, session: AsyncSession):
    """Update a board column."""
    return await board_repository.update_board_column(
        column_id=column_id,
        updated_data=column_data.model_dump(exclude_none=True),
        session=session,
    )


async def delete_board_column(column_id: UUID, session: AsyncSession) -> None:
    """Delete a board column."""
    await board_repository.delete_board_column(
        column_id=column_id,
        session=session,
    )


# Event service methods

async def create_board_event(event_data, created_by_id: UUID, session: AsyncSession):
    """Create a board event/milestone."""
    from shared_models.dtos.board_event_in_dto import BoardEventCreateDTO
    event_payload = event_data.model_dump(exclude_none=True)
    event_payload['created_by_id'] = created_by_id
    event_payload['version'] = 1
    return await board_repository.create_board_event(
        event_payload,
        session=session,
    )


async def get_board_event_by_id(
    event_id: UUID, session: AsyncSession
) -> BoardEventOutDTO:
    return serialize_board_event_as_dto(
        await board_repository.get_board_event_by_id(event_id=event_id, session=session)
    )


async def get_board_events_by_board_id(
    board_id: UUID, session: AsyncSession
) -> list[BoardEventOutDTO]:
    return [
        serialize_board_event_as_dto(event)
        for event in await board_repository.get_board_events_by_board_id(
            board_id=board_id,
            session=session,
        )
    ]


async def update_board_event(event_id: UUID, event_data, session: AsyncSession):
    """Update a board event."""
    return await board_repository.update_board_event(
        event_id=event_id,
        updated_data=event_data.model_dump(exclude_none=True),
        session=session,
    )


async def delete_board_event(event_id: UUID, session: AsyncSession) -> None:
    """Delete a board event."""
    await board_repository.delete_board_event(
        event_id=event_id,
        session=session,
    )


# Permission service methods

async def add_user_to_board(permission_data, session: AsyncSession):
    """Add a user to a board with a specific role."""
    permission_payload = permission_data
    return await board_repository.add_user_to_board(
        permission_payload,
        session=session,
    )


async def get_board_permission(
    board_id: UUID, user_id: UUID, session: AsyncSession
) -> BoardPermissionOutDTO:
    return serialize_board_permission_as_dto(
        await board_repository.get_board_permission(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
    )


async def get_board_permissions_by_board_id(
    board_id: UUID, session: AsyncSession
) -> list[BoardPermissionOutDTO]:
    return [
        serialize_board_permission_as_dto(permission)
        for permission in await board_repository.get_board_permissions_by_board_id(
            board_id=board_id,
            session=session,
        )
    ]


async def update_user_board_permission(
    board_id: UUID, user_id: UUID, permission_data, session: AsyncSession
):
    """Update a user's role in a board."""
    return await board_repository.update_user_board_permission(
        board_id=board_id,
        user_id=user_id,
        updated_data=permission_data.model_dump(exclude_none=True),
        session=session,
    )


async def remove_user_from_board(board_id: UUID, user_id: UUID, session: AsyncSession) -> None:
    """Remove a user from a board."""
    await board_repository.remove_user_from_board(
        board_id=board_id,
        user_id=user_id,
        session=session,
    )
