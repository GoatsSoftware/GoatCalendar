from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from database_service.database import get_db_session
from shared_models.dtos.board_permission_in_dto import BoardPermissionCreateDTO, BoardPermissionUpdateDTO
from board_service.services import board_service


route = APIRouter(prefix="/boards", tags=["board-permissions"])
db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


@route.post("/{board_id}/permissions")
async def add_user_to_board(
    board_id: UUID,
    permission_data: BoardPermissionCreateDTO,
):
    """Add a user to a board with a specific role."""
    try:
        permission_payload = permission_data.model_dump(exclude_none=True)
        permission_payload['board_id'] = board_id
        return await board_service.add_user_to_board(
            permission_data=permission_payload,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.put("/{board_id}/permissions/{user_id}")
async def update_user_board_permission(
    board_id: UUID,
    user_id: UUID,
    permission_data: BoardPermissionUpdateDTO,
):
    """Update a user's role in a board."""
    try:
        return await board_service.update_user_board_permission(
            board_id=board_id,
            user_id=user_id,
            permission_data=permission_data,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Permission not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.delete("/{board_id}/permissions/{user_id}")
async def remove_user_from_board(
    board_id: UUID,
    user_id: UUID,
):
    """Remove a user from a board."""
    try:
        await board_service.remove_user_from_board(
            board_id=board_id,
            user_id=user_id,
            session=session,
        )
        return Response(status_code=204)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Permission not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
