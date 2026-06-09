from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from database_service.database import get_session
from shared_models.dtos.board_event_in_dto import BoardEventCreateDTO, BoardEventUpdateDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from auth_service.routes.authentication_route import get_current_user
from board_service.services import board_service


route = APIRouter(prefix="/board-events", tags=["board-events"])


@route.post("")
async def create_board_event(
    event_data: BoardEventCreateDTO,
    current_user: UserAuthDTO = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new board event/milestone."""
    try:
        return await board_service.create_board_event(
            event_data=event_data,
            created_by_id=current_user.id,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.put("/{event_id}")
async def update_board_event(
    event_id: UUID,
    event_data: BoardEventUpdateDTO,
    session: AsyncSession = Depends(get_session),
):
    """Update a board event."""
    try:
        return await board_service.update_board_event(
            event_id=event_id,
            event_data=event_data,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@route.delete("/{event_id}")
async def delete_board_event(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Delete a board event."""
    try:
        await board_service.delete_board_event(
            event_id=event_id,
            session=session,
        )
        return Response(status_code=204)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
