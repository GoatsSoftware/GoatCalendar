from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_permission_in_dto import (
    BoardPermissionCreateDTO,
    BoardPermissionUpdateDTO,
)
from shared_models.dtos.board_permission_out_dto import BoardPermissionOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_service


route = APIRouter(
    prefix="/boards",
    tags=["board-permissions"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]
PERMISSION_NOT_FOUND_DETAIL = "Permission not found"


@route.get(
    "/{board_id}/permissions",
    status_code=status.HTTP_200_OK,
)
async def get_board_permissions(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardPermissionOutDTO]:
    """
    HTTP GET endpoint to fetch all permissions attached to a board.

    :param board_id: The UUID of the parent board.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching board permission DTOs.
    """
    return await board_service.get_board_permissions_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.get(
    "/{board_id}/permissions/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def get_board_permission(
    board_id: UUID,
    user_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardPermissionOutDTO:
    """
    HTTP GET endpoint to fetch a specific board permission.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching board permission DTO.
    :raises HTTPException: 404 error if the permission does not exist.
    """
    try:
        return await board_service.get_board_permission(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PERMISSION_NOT_FOUND_DETAIL,
        ) from exception


@route.post("/{board_id}/permissions", status_code=status.HTTP_201_CREATED)
async def add_user_to_board(
    board_id: UUID,
    permission_data: BoardPermissionCreateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    """
    HTTP POST endpoint to grant a user access to a board.

    :param board_id: The UUID of the target board.
    :param permission_data: The validated payload describing the granted role.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The newly created permission model.
    """
    permission_payload = permission_data.model_dump(exclude_none=True)
    permission_payload["board_id"] = board_id
    return await board_service.add_user_to_board(
        permission_data=permission_payload,
        session=session,
    )


@route.put("/{board_id}/permissions/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_board_permission(
    board_id: UUID,
    user_id: UUID,
    permission_data: BoardPermissionUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    """
    HTTP PUT endpoint to update a user's role on a board.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param permission_data: The validated payload containing updated role data.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The updated permission model.
    :raises HTTPException: 404 error if the permission does not exist.
    """
    try:
        return await board_service.update_user_board_permission(
            board_id=board_id,
            user_id=user_id,
            permission_data=permission_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PERMISSION_NOT_FOUND_DETAIL,
        ) from exception


@route.delete("/{board_id}/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_board(
    board_id: UUID,
    user_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    """
    HTTP DELETE endpoint to remove a user's permission from a board.

    :param board_id: The UUID of the target board.
    :param user_id: The UUID of the target user.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: An empty HTTP 204 response.
    :raises HTTPException: 404 error if the permission does not exist.
    """
    try:
        await board_service.remove_user_from_board(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PERMISSION_NOT_FOUND_DETAIL,
        ) from exception
