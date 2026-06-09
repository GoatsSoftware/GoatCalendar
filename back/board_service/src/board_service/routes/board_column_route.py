from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from database_service.database import get_db_session
from shared_models.dtos.board_column_in_dto import BoardColumnCreateDTO, BoardColumnUpdateDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from auth_service.routes.authentication_route import get_current_user
from board_service.services import board_service


route = APIRouter(prefix="/board-columns", tags=["board-columns"])
db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


@route.post("")
async def create_board_column(
    column_data: BoardColumnCreateDTO,
    current_user: UserAuthDTO = Depends(get_current_user),
):
    """Create a new board column."""
    try:
        return await board_service.create_board_column(
            column_data=column_data,
            created_by_id=current_user.id,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.put("/{column_id}")
async def update_board_column(
    column_id: UUID,
    column_data: BoardColumnUpdateDTO,
):
    """Update a board column."""
    try:
        return await board_service.update_board_column(
            column_id=column_id,
            column_data=column_data,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Column not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.delete("/{column_id}")
async def delete_board_column(
    column_id: UUID,
):
    """Delete a board column."""
    try:
        await board_service.delete_board_column(
            column_id=column_id,
            session=session,
        )
        return Response(status_code=204)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Column not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
