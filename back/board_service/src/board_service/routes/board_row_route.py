from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_row_in_dtos import BoardRowCreateDTO, BoardRowUpdateDTO
from shared_models.dtos.board_row_out_dto import BoardRowOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import BoardRow
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_row_service

route = APIRouter(
    prefix="/board-rows",
    tags=["board-rows"],
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
) -> BoardRow:
    """
    HTTP GET endpoint to fetch a single board row by its unique ID.

    :param board_row_id: The UUID of the board row.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching row data transfer object.
    :raises HTTPException: 404 error if the board row does not exist.
    """
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
) -> list[BoardRow]:
    """
    HTTP GET endpoint to fetch all rows matching a specific board ID.

    :param board_id: The UUID of the target board.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching rows formatted as DTOs.
    :raises HTTPException: 404 error if the board does not exist.
    """
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


@route.post("", response_model=BoardRowOutDTO, status_code=status.HTTP_201_CREATED)
async def create_board_row(
    board_row_data: BoardRowCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> BoardRow:
    """HTTP POST endpoint to create a new board row."""
    return await board_row_service.create_board_row(
        board_row_data=board_row_data,
        created_by_id=current_user.id,
        session=session,
    )


@route.put(
    "/{board_row_id}",
    response_model=BoardRowOutDTO,
    status_code=status.HTTP_200_OK,
)
async def update_board_row(
    board_row_id: UUID,
    board_row_data: BoardRowUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardRow:
    """HTTP PUT endpoint to update an existing board row."""
    try:
        return await board_row_service.update_board_row(
            board_row_id=board_row_id,
            board_row_data=board_row_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board row '{board_row_id}' not found",
        ) from exception


@route.delete("/{board_row_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_row(
    board_row_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    """HTTP DELETE endpoint to remove a board row."""
    try:
        await board_row_service.delete_board_row(
            board_row_id=board_row_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board row '{board_row_id}' not found",
        ) from exception
