from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_row_task_in_dto import (
    BoardRowTaskCreateDTO,
    BoardRowTaskUpdateDTO,
)
from shared_models.dtos.board_row_task_out_dto import BoardRowTaskOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import BoardRowTask
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_row_service
from board_service.services.exceptions import ConcurrencyException

route = APIRouter(
    prefix="/board-row-tasks",
    tags=["board-row-tasks"],
    responses={404: {"description": "Not found"}},
)


user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]
db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


@route.post("", response_model=BoardRowTaskOutDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: BoardRowTaskCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> BoardRowTask:
    return await board_row_service.create_board_row_task(
        task_data=task_data, created_by_id=current_user.id, session=session
    )


@route.get("/{task_id}", response_model=BoardRowTaskOutDTO, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    task_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardRowTask:
    try:
        return await board_row_service.get_board_row_task_by_id(
            task_id=task_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        ) from exception


@route.get(
    "/board-row/{board_row_id}",
    response_model=list[BoardRowTaskOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_tasks_by_board_row_id(
    board_row_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardRowTask]:
    return await board_row_service.get_board_row_tasks_by_board_row_id(
        board_row_id=board_row_id,
        session=session,
    )


@route.get(
    "/board-column/{board_column_id}",
    response_model=list[BoardRowTaskOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_tasks_by_board_column_id(
    board_column_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardRowTask]:
    return await board_row_service.get_board_row_tasks_by_board_column_id(
        board_column_id=board_column_id,
        session=session,
    )


@route.put("/{task_id}", response_model=BoardRowTaskOutDTO, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: UUID,
    task_data: BoardRowTaskUpdateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> BoardRowTask:
    try:
        return await board_row_service.update_board_row_task(
            task_id=task_id, task_data=task_data, session=session
        )
    except ConcurrencyException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This task has been modified by another user. Please refresh the board.",
        )
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        ) from exception


@route.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: db_session_dependency,
    current_user: user_connected_dependency,
) -> Response:
    try:
        await board_row_service.delete_board_row_task(task_id=task_id, session=session)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        ) from exception
