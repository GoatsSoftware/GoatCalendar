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


@route.get(
    "/{board_id}/permissions",
    response_model=list[BoardPermissionOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_board_permissions(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardPermissionOutDTO]:
    return await board_service.get_board_permissions_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.get(
    "/{board_id}/permissions/{user_id}",
    response_model=BoardPermissionOutDTO,
    status_code=status.HTTP_200_OK,
)
async def get_board_permission(
    board_id: UUID,
    user_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardPermissionOutDTO:
    try:
        return await board_service.get_board_permission(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found") from exception


@route.post("/{board_id}/permissions", status_code=status.HTTP_201_CREATED)
async def add_user_to_board(
    board_id: UUID,
    permission_data: BoardPermissionCreateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
):
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
    try:
        return await board_service.update_user_board_permission(
            board_id=board_id,
            user_id=user_id,
            permission_data=permission_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found") from exception


@route.delete("/{board_id}/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_board(
    board_id: UUID,
    user_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    try:
        await board_service.remove_user_from_board(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found") from exception
