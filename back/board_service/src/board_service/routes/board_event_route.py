from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_event_in_dto import BoardEventCreateDTO, BoardEventUpdateDTO
from shared_models.dtos.board_event_out_dto import BoardEventOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
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
    return await board_service.get_board_events_by_board_id(
        board_id=board_id,
        session=session,
    )


@route.post("", status_code=status.HTTP_201_CREATED)
async def create_board_event(
    event_data: BoardEventCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
):
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
):
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
