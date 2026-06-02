from typing import Annotated

from database_service.database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.models.jwt_tokens import JWTTokens
from sqlalchemy.exc import NoResultFound
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.services.authentication_service import (
    check_auth_user,
    login,
    refresh_access_token,
)

route = APIRouter(
    prefix="/authentication",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/auth", auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

db_session_dependency = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: db_session_dependency,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> UserAuthDTO:
    """
    Extracts and validates the authenticated user from a Bearer token.

    This dependency is used to protect routes by ensuring the request
    contains a valid access token. It verifies the token against the
    database and returns the corresponding user data transfer object.

    :param session: The active asynchronous database session.
    :param token: The JWT access token extracted from the Authorization header if provided.
    :return: A DTO containing the authenticated user's information.
    """
    if token is None:
        raise credentials_exception

    try:
        return await check_auth_user(
            access_token=token,
            session=session,
        )
    except (NoResultFound, ValueError) as exception:
        raise credentials_exception from exception


@route.post("/auth", response_model=JWTTokens, status_code=status.HTTP_201_CREATED)
async def authenticate_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: db_session_dependency,
) -> JWTTokens:
    """
    Validates user credentials and issues a new pair of JWT tokens.

    This endpoint processes standard OAuth2 password request forms,
    verifying the username and password against the identity provider.
    Upon success, it generates both an access token and a refresh token.

    :param credentials: The username and password submitted via the login form.
    :param session: The active asynchronous database session.
    :return: An object containing the new access and refresh tokens.
    """
    try:
        return await login(
            credentials=credentials,
            session=session,
        )
    except (NoResultFound, ValueError) as exception:
        raise credentials_exception from exception


@route.post(
    "/refresh-access-token",
    response_model=UserAuthDTO,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_user_access_token(
    refresh_token: str,
    session: db_session_dependency,
) -> UserAuthDTO:
    """
    Renews an expired access token using a valid refresh token.

    This function allows users to maintain their session without
    re-entering credentials, provided they possess a legitimate
    and unexpired refresh token.

    :param refresh_token: The persistent token used to request a new access token.
    :param session: The active asynchronous database session.
    :return: The user information associated with the refreshed session.
    """
    try:
        return await refresh_access_token(
            refresh_token=refresh_token,
            session=session,
        )
    except (NoResultFound, ValueError) as exception:
        raise credentials_exception from exception


@route.get("/me", response_model=UserAuthDTO, status_code=status.HTTP_200_OK)
async def me(
    user: Annotated[UserAuthDTO, Depends(get_current_user)],
) -> UserAuthDTO:
    """
    Retrieves the identity details of the currently logged-in user.

    This endpoint acts as a protected profile check, returning the
    authenticated user's data after successfully passing through
     the token validation dependency.

    :param user: The user object injected by the get_current_user dependency.
    :return: The data transfer object of the currently authenticated user.
    """
    try:
        return user
    except (NoResultFound, ValueError) as exception:
        raise credentials_exception from exception
