from typing import Annotated

from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.dtos.user_dtos import UserInDTO, UserOutDTO
from shared_models.dtos.user_search_query_dto import UserSearchQueryDTO
from sqlalchemy.exc import NoResultFound
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from auth_service.routes.authentication_route import get_current_user
from auth_service.services import user_service

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
    response_model=list[UserOutDTO],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    session: db_session_dependency,
) -> list[UserOutDTO]:
    """
    HTTP GET endpoint to fetch a complete list of all registered users.

    :param session: The injected asynchronous database session dependency.
    :return: A response list containing all users.
    """
    return await user_service.get_all_users(session)


@route.get(
    "/search",
    response_model=list[UserOutDTO],
    status_code=status.HTTP_200_OK,
)
async def search_users(
    search_query: search_users_query_dependency,
    session: db_session_dependency,
) -> list[UserOutDTO]:
    """
    HTTP GET endpoint to search users by name or email.

    :param search_query: The validated query parameters for the search operation.
    :param session: The injected asynchronous database session dependency.
    :return: A list of users matching the search query.
    """
    return await user_service.search_users(search_query.q, session)


@route.put(
    "/me",
    response_model=UserOutDTO,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid user update payload"},
        404: {"description": USER_NOT_FOUND_DETAIL},
    },
)
async def update_me(
    user_update: UserInDTO,
    session: db_session_dependency,
    current_user: current_user_dependency,
) -> UserOutDTO:
    """
    HTTP PUT endpoint to update the profile of the authenticated user.

    :param user_update: The raw payload containing profile fields to update.
    :param session: The injected asynchronous database session dependency.
    :param current_user: The authenticated user dependency.
    :return: The updated user model.
    :raises HTTPException: 404 error if the user does not exist.
    :raises HTTPException: 400 error if the payload is invalid.
    """
    try:
        return await user_service.update_user(current_user.id, user_update, session)
    except NoResultFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_DETAIL,
        ) from exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
