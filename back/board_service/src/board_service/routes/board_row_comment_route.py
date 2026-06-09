from typing import Annotated
from uuid import UUID

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared_models.dtos.board_row_comment_in_dto import (
    BoardRowCommentCreateDTO,
    BoardRowCommentUpdateDTO,
)
from shared_models.dtos.board_row_comment_out_dto import BoardRowCommentOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.schemas import BoardRowComment
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from board_service.services import board_row_service


route = APIRouter(
    prefix="/board-row-comments",
    tags=["board-row-comments"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
user_connected_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]


@route.get(
    "/{comment_id}",
    response_model=BoardRowCommentOutDTO,
    status_code=status.HTTP_200_OK,
)
async def get_board_row_comment_by_id(
    comment_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> BoardRowComment:
    try:
        return await board_row_service.get_board_row_comment_by_id(
            comment_id=comment_id,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found") from exception


@route.get(
    "/board-row/{board_row_id}",
    response_model=list[BoardRowCommentOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_board_row_comments_by_board_row_id(
    board_row_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> list[BoardRowComment]:
    return await board_row_service.get_board_row_comments_by_board_row_id(
        board_row_id=board_row_id,
        session=session,
    )


@route.post("", status_code=status.HTTP_201_CREATED)
async def create_board_row_comment(
    comment_data: BoardRowCommentCreateDTO,
    session: db_session_dependency,
    current_user: user_connected_dependency,
):
    return await board_row_service.create_board_row_comment(
        comment_data=comment_data,
        created_by_id=current_user.id,
        session=session,
    )


@route.put("/{comment_id}", status_code=status.HTTP_200_OK)
async def update_board_row_comment(
    comment_id: UUID,
    comment_data: BoardRowCommentUpdateDTO,
    session: db_session_dependency,
    _: user_connected_dependency,
):
    try:
        return await board_row_service.update_board_row_comment(
            comment_id=comment_id,
            comment_data=comment_data,
            session=session,
        )
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found") from exception


@route.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_row_comment(
    comment_id: UUID,
    session: db_session_dependency,
    _: user_connected_dependency,
) -> Response:
    try:
        await board_row_service.delete_board_row_comment(
            comment_id=comment_id,
            session=session,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoResultFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found") from exception
