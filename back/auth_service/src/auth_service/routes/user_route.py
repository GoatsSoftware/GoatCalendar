from typing import Annotated

from database_service.database import get_db_session
from fastapi import APIRouter, Depends
from shared_models.schemas import User
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from auth_service.services import user_service

route = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Depends(get_db_session)


@route.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=list[User],
)
async def get_all_users(
    session: Annotated[AsyncSession, db_session_dependency],
) -> list[User]:
    """ """
    return await user_service.get_all_users(session)
