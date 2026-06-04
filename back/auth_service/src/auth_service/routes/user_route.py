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

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


@route.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[User],
)
async def get_all_users(
    session: db_session_dependency,
) -> list[User]:
    """
    HTTP GET endpoint to fetch a complete list of all registered users.

    :param session: The injected asynchronous database session dependency.
    :return: A response list containing all users.
    """
    return await user_service.get_all_users(session)
