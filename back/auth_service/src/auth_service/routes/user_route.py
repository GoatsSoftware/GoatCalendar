from typing import Annotated

from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException
from auth_service.routes.authentication_route import get_current_user
from auth_service.services import user_service
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.dtos.user_search_query_dto import UserSearchQueryDTO
from shared_models.schemas import User
from sqlalchemy.exc import NoResultFound
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

route = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]
current_user_dependency = Annotated[UserAuthDTO, Depends(get_current_user)]
search_users_query_dependency = Annotated[UserSearchQueryDTO, Depends()]
USER_NOT_FOUND_DETAIL = "User not found"


@route.get(
    "",
    status_code=status.HTTP_200_OK,
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


@route.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    current_user: current_user_dependency,
) -> UserAuthDTO:
    """Get the authenticated user's profile."""
    return current_user


@route.get(
    "/search",
    status_code=status.HTTP_200_OK,
)
async def search_users(
    search_query: search_users_query_dependency,
    session: db_session_dependency,
) -> list[User]:
    """Search for users by name or email."""
    return await user_service.search_users(search_query.q, session)


@route.put(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid user update payload"},
        404: {"description": USER_NOT_FOUND_DETAIL},
    },
)
async def update_me(
    user_update: dict,
    session: db_session_dependency,
    current_user: current_user_dependency,
) -> User:
    """Update current user's profile (limited fields like display name)."""
    try:
        return await user_service.update_user(current_user.id, user_update, session)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_DETAIL,
        ) from exception
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
