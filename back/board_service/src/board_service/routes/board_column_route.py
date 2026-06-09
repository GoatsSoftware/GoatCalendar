from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_column_in_dto import BoardColumnCreateDTO, BoardColumnUpdateDTO
from shared_models.dtos.board_column_out_dto import BoardColumnOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import BoardColumn
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_service


route = APIRouter(
    prefix="/board-columns",
    tags=["board-columns"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]


@route.get(
    "/board/{board_id}",
    response_model=list[BoardColumnOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_board_columns_by_board_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardColumn]:
    return await board_service.get_board_columns_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.get("/{column_id}", response_model=BoardColumnOutDTO, status_code=status.HTTP_200_OK)
async def get_board_column_by_id(
    column_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardColumn:
    try:
        return await board_service.get_board_column_by_id(
            column_id=column_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found") from exception


@route.post("", status_code=status.HTTP_201_CREATED)
async def create_board_column(
    column_data: BoardColumnCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
):
    return await board_service.create_board_column(
        column_data=column_data,
        created_by_id=current_user.id,
        session=session,
    )


@route.put("/{column_id}", status_code=status.HTTP_200_OK)
async def update_board_column(
    column_id: UUID,
    column_data: BoardColumnUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_service.update_board_column(
            column_id=column_id,
            column_data=column_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found") from exception


@route.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_column(
    column_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    try:
        await board_service.delete_board_column(
            column_id=column_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found") from exception
