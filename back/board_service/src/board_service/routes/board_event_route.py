from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_event_in_dto import (
    BoardEventCreateDTO,
    BoardEventUpdateDTO,
)
from shared_models.dtos.board_event_out_dto import BoardEventOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import BoardEvent
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_service

route = APIRouter(
    prefix="/board-events",
    tags=["board-events"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]
EVENT_NOT_FOUND_DETAIL = "Event not found"


@route.get("/{event_id}", status_code=status.HTTP_200_OK)
async def get_board_event_by_id(
    event_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardEventOutDTO:
    """
    HTTP GET endpoint to fetch a single board event by its ID.

    :param event_id: The UUID of the requested event.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching board event DTO.
    :raises HTTPException: 404 error if the event does not exist.
    """
    try:
        return await board_service.get_board_event_by_id(
            event_id=event_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVENT_NOT_FOUND_DETAIL,
        ) from exception


@route.get(
    "/board/{board_id}",
    status_code=status.HTTP_200_OK,
)
async def get_board_events_by_board_id(
    board_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardEventOutDTO]:
    """
    HTTP GET endpoint to fetch all events belonging to a board.

    :param board_id: The UUID of the parent board.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching board event DTOs.
    """
    return await board_service.get_board_events_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.post("", status_code=status.HTTP_201_CREATED)
async def create_board_event(
    event_data: BoardEventCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> BoardEvent:
    """
    HTTP POST endpoint to create a new board event.

    :param event_data: The validated payload describing the new event.
    :param session: The injected database session.
    :param current_user: The authenticated user creating the event.
    :return: The newly created board event model.
    """
    return await board_service.create_board_event(
        event_data=event_data,
        created_by_id=current_user.id,
        session=session,
    )


@route.put("/{event_id}", status_code=status.HTTP_200_OK)
async def update_board_event(
    event_id: UUID,
    event_data: BoardEventUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardEvent:
    """
    HTTP PUT endpoint to update an existing board event.

    :param event_id: The UUID of the event to update.
    :param event_data: The validated payload containing updated event values.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The updated board event model.
    :raises HTTPException: 404 error if the event does not exist.
    """
    try:
        return await board_service.update_board_event(
            event_id=event_id,
            event_data=event_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVENT_NOT_FOUND_DETAIL,
        ) from exception


@route.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_event(
    event_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    """
    HTTP DELETE endpoint to remove a board event.

    :param event_id: The UUID of the event to delete.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: An empty HTTP 204 response.
    :raises HTTPException: 404 error if the event does not exist.
    """
    try:
        await board_service.delete_board_event(
            event_id=event_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVENT_NOT_FOUND_DETAIL,
        ) from exception
