from typing import Annotated

from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException
from shared_models.schemas import User
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from sqlalchemy.exc import NoResultFound

from auth_service.services import user_service
from shared_models.dtos.user_auth_dto import UserAuthDTO
from auth_service.routes.authentication_route import get_current_user

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


@route.get("/me", status_code=status.HTTP_200_OK, response_model=User)
async def get_me(
    current_user: UserAuthDTO = Depends(get_current_user),
    session: db_session_dependency = Depends(get_db_session),
) -> User:
    """Get the authenticated user's profile."""
    return current_user


@route.get("/search", status_code=status.HTTP_200_OK, response_model=list[User])
async def search_users(
    q: str,
    session: db_session_dependency,
) -> list[User]:
    """Search for users by name or email."""
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters",
        )
    return await user_service.search_users(q, session)


@route.put("/me", status_code=status.HTTP_200_OK, response_model=User)
async def update_me(
    user_update: dict,
    current_user: UserAuthDTO = Depends(get_current_user),
    session: db_session_dependency = Depends(get_db_session),
) -> User:
    """Update current user's profile (limited fields like display name)."""
    try:
        return await user_service.update_user(current_user.id, user_update, session)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
