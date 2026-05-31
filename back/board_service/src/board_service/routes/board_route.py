from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_service

route = APIRouter(
    prefix="/board",
    tags=["board"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]


@route.get("", response_model=list[BoardOutDTO], status_code=status.HTTP_200_OK)
async def get_all_boards(session: db_session_dependency, _: user_connected_dependency):
    return await board_service.get_all_boards(session=session)


@route.get("/{board_id}", response_model=BoardOutDTO, status_code=status.HTTP_200_OK)
async def get_board_by_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_service.get_board_by_id(board_id=board_id, session=session)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board '{board_id}' not found",
        ) from exception


@route.get(
    "/user/{user_id}",
    response_model=list[BoardOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_user_boards(
    user_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_service.get_user_boards(user_id=user_id, session=session)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        ) from exception
