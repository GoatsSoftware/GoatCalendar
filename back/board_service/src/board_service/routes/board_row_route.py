from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from shared_models.dtos.board_row_out_dto import BoardRowOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_row_service

route = APIRouter(
    prefix="/board_row",
    tags=["board_row"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]


@route.get(
    "/{board_row_id}",
    response_model=BoardRowOutDTO,
    status_code=status.HTTP_200_OK,
)
async def get_board_rows_by_id(
    board_row_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_row_service.get_board_row_by_id(
            board_row_id=board_row_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board row '{board_row_id}' not found",
        ) from exception


@route.get(
    "/board/{board_id}",
    response_model=list[BoardRowOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_board_rows_by_board_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_row_service.get_board_rows_by_board_id(
            board_id=board_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board '{board_id}' not found",
        ) from exception
