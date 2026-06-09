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
from shared_models.exceptions import ConcurrencyException
from shared_models.schemas import BoardRowTask
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_row_service

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
    """
    HTTP POST endpoint to create a new task within a board row.

    :param task_data: The validated payload describing the new task.
    :param session: The injected database session.
    :param current_user: The authenticated user creating the task.
    :return: The newly created task model.
    """
    return await board_row_service.create_board_row_task(
        task_data=task_data, created_by_id=current_user.id, session=session
    )


@route.get("/{task_id}", response_model=BoardRowTaskOutDTO, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    task_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardRowTask:
    """
    HTTP GET endpoint to fetch a single task by its ID.

    :param task_id: The UUID of the requested task.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: The matching task data transfer object.
    :raises HTTPException: 404 error if the task does not exist.
    """
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
    """
    HTTP GET endpoint to fetch all tasks belonging to a board row.

    :param board_row_id: The UUID of the parent board row.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching task data transfer objects.
    """
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
    """
    HTTP GET endpoint to fetch all tasks attached to a board column.

    :param board_column_id: The UUID of the parent board column.
    :param session: The injected database session.
    :param _: The authenticated user dependency.
    :return: A list of matching task data transfer objects.
    """
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
    """
    HTTP PUT endpoint to update an existing task.

    :param task_id: The UUID of the task to update.
    :param task_data: The validated payload containing updated task values.
    :param session: The injected database session.
    :param current_user: The authenticated user dependency.
    :return: The updated task model.
    :raises HTTPException: 404 error if the task does not exist.
    :raises HTTPException: 409 error if the task version is stale.
    """
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
    """
    HTTP DELETE endpoint to remove a task.

    :param task_id: The UUID of the task to delete.
    :param session: The injected database session.
    :param current_user: The authenticated user dependency.
    :return: An empty HTTP 204 response.
    :raises HTTPException: 404 error if the task does not exist.
    """
    try:
        await board_row_service.delete_board_row_task(task_id=task_id, session=session)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        ) from exception
