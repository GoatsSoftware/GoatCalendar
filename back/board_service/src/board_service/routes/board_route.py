from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_in_dtos import BoardCreateDTO, BoardUpdateDTO
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import Board
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_service

route = APIRouter(
    prefix="/boards",
    tags=["boards"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]


@route.get("", response_model=list[BoardOutDTO], status_code=status.HTTP_200_OK)
async def get_all_boards(
    session: db_session_dependency, _: user_connected_dependency,
) -> list[Board]:
    """
    HTTP GET endpoint to fetch a list of all existing boards.

    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of all boards formatted as DTOs.
    """
    return await board_service.get_all_boards(session=session)


@route.get("/{board_id}", response_model=BoardOutDTO, status_code=status.HTTP_200_OK)
async def get_board_by_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Board:
    """
    HTTP GET endpoint to fetch a single board configuration by its ID.

    :param board_id: The UUID of the requested board.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching board data transfer object.
    :raises HTTPException: 404 error if the board does not exist.
    """
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
) -> list[Board]:
    """
    HTTP GET endpoint to fetch all boards belonging to a specific user.

    :param user_id: The UUID of the target user.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of boards matching the owner.
    :raises HTTPException: 404 error if the user record cannot be verified.
    """
    try:
        return await board_service.get_user_boards(user_id=user_id, session=session)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        ) from exception


@route.post("", response_model=BoardOutDTO, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> Board:
    """HTTP POST endpoint to create a new board."""
    return await board_service.create_board(
        board_data=board_data,
        created_by_id=current_user.id,
        session=session,
    )


@route.put("/{board_id}", response_model=BoardOutDTO, status_code=status.HTTP_200_OK)
async def update_board(
    board_id: UUID,
    board_data: BoardUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Board:
    """HTTP PUT endpoint to update an existing board."""
    try:
        return await board_service.update_board(
            board_id=board_id,
            board_data=board_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board '{board_id}' not found",
        ) from exception


@route.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    """HTTP DELETE endpoint to remove a board."""
    try:
        await board_service.delete_board(board_id=board_id, session=session)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board '{board_id}' not found",
        ) from exception
