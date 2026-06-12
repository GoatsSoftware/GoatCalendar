from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_column_in_dto import (
    BoardColumnCreateDTO,
    BoardColumnUpdateDTO,
)
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
COLUMN_NOT_FOUND_DETAIL = "Column not found"


@route.get(
    "/board/{board_id}",
    status_code=status.HTTP_200_OK,
)
async def get_board_columns_by_board_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardColumn]:
    """
    HTTP GET endpoint to fetch all columns belonging to a board.

    :param board_id: The UUID of the parent board.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching board column DTOs.
    """
    return await board_service.get_board_columns_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.get("/{column_id}", status_code=status.HTTP_200_OK)
async def get_board_column_by_id(
    column_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardColumn:
    """
    HTTP GET endpoint to fetch a single board column by its ID.

    :param column_id: The UUID of the requested column.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching board column DTO.
    :raises HTTPException: 404 error if the column does not exist.
    """
    try:
        return await board_service.get_board_column_by_id(
            column_id=column_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLUMN_NOT_FOUND_DETAIL,
        ) from exception


@route.post("", status_code=status.HTTP_201_CREATED)
async def create_board_column(
    column_data: BoardColumnCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> BoardColumn:
    """
    HTTP POST endpoint to create a new board column.

    :param column_data: The validated payload describing the new column.
    :param session: The injected database session.
    :param current_user: The authenticated user creating the column.
    :return: The newly created board column model.
    """
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
) -> BoardColumn:
    """
    HTTP PUT endpoint to update an existing board column.

    :param column_id: The UUID of the column to update.
    :param column_data: The validated payload containing updated column values.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The updated board column model.
    :raises HTTPException: 404 error if the column does not exist.
    """
    try:
        return await board_service.update_board_column(
            column_id=column_id,
            column_data=column_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLUMN_NOT_FOUND_DETAIL,
        ) from exception


@route.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_column(
    column_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    """
    HTTP DELETE endpoint to remove a board column.

    :param column_id: The UUID of the column to delete.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: An empty HTTP 204 response.
    :raises HTTPException: 404 error if the column does not exist.
    """
    try:
        await board_service.delete_board_column(
            column_id=column_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLUMN_NOT_FOUND_DETAIL,
        ) from exception
