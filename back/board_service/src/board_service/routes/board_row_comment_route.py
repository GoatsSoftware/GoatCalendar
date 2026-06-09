from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from database_service.database import get_db_session
from shared_models.dtos.board_row_comment_in_dto import BoardRowCommentCreateDTO, BoardRowCommentUpdateDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from auth_service.routes.authentication_route import get_current_user
from board_service.services import board_row_service


route = APIRouter(prefix="/board-row-comments", tags=["board-row-comments"])
db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


@route.post("")
async def create_board_row_comment(
    comment_data: BoardRowCommentCreateDTO,
    current_user: UserAuthDTO = Depends(get_current_user),
    session: db_session_dependency = Depends(get_db_session),
):
    """Create a new comment on a board row."""
    try:
        return await board_row_service.create_board_row_comment(
            comment_data=comment_data,
            created_by_id=current_user.id,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.put("/{comment_id}")
async def update_board_row_comment(
    comment_id: UUID,
    comment_data: BoardRowCommentUpdateDTO,
    session: db_session_dependency = Depends(get_db_session),
):
    """Update a board row comment."""
    try:
        return await board_row_service.update_board_row_comment(
            comment_id=comment_id,
            comment_data=comment_data,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Comment not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.delete("/{comment_id}")
async def delete_board_row_comment(
    comment_id: UUID,
    session: db_session_dependency = Depends(get_db_session),
):
    """Delete a board row comment."""
    try:
        await board_row_service.delete_board_row_comment(
            comment_id=comment_id,
            session=session,
        )
        return Response(status_code=204)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Comment not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
