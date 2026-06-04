from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.enums import TokenType
from shared_models.models.auth_settings import get_auth_settings
from shared_models.models.jwt_tokens import JWTTokens
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.repositories import user_repository
from auth_service.utils.hash import compare_text_with_hash
from auth_service.utils.jwt import create_token, decode_jwt_token

AUTH_SETTINGS = get_auth_settings()


async def login(
    credentials: OAuth2PasswordRequestForm,
    session: AsyncSession,
) -> JWTTokens:
    """
    Verifies user identity and generates an initial set of security tokens.

    The function performs a two-step validation: first confirming the existence
    of the user by email, then comparing the provided password against the
    stored cryptographic hash. Upon success, it issues a pair of JWTs with
    predefined expiration windows.

    :param credentials: The login form containing the username and plain-text password.
    :param session: The active asynchronous database session.
    :return: A JWTTokens object containing the new access and refresh tokens.
    """
    # check user exists in db
    user = await user_repository.get_user_by_email_address(
        email_address=credentials.username,
        session=session,
    )

    # check password provided corresponds to password in db
    if not compare_text_with_hash(
        plain_text=credentials.password,
        text_hashed=user.password,
    ):
        raise ValueError(
            "Provided password does not match hashed password in db for user",
        )

    # credentials provided are correct, create jwt tokens
    access_token_expires = timedelta(
        minutes=AUTH_SETTINGS.access_token_duration_minutes,
    )
    refresh_token_expires = timedelta(hours=AUTH_SETTINGS.refresh_token_duration_hours)
    access_token = create_token(
        data={"sub": user.email_address, "token_type": TokenType.ACCESS},
        expires_delta=access_token_expires,
    )
    refresh_token = create_token(
        data={"sub": user.email_address, "token_type": TokenType.REFRESH},
        expires_delta=refresh_token_expires,
    )

    return JWTTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        auth_schema="bearer",
    )


async def check_auth_user(access_token: str, session: AsyncSession) -> UserAuthDTO:
    """
    Validates an access token and retrieves the associated user profile.

    This function decodes the JWT to verify its signature and integrity. It
    specifically checks that the token is of the 'access' type before
    fetching the user's latest data and location from the database to
    construct a complete authorization DTO.

    :param access_token: The encoded JWT string to be validated.
    :param session: The active asynchronous database session.
    :return: A UserAuthDTO containing the user's profile and the current token.
    """
    # decode token
    try:
        payload = decode_jwt_token(
            token=access_token,
        )
    except JWTError as exception:
        raise ValueError(
            "Unable to decode provided jwt token access token",
        ) from exception

    # retrieve user email address in decoded token
    try:
        email_address = payload.get("sub")
        token_type = payload.get("token_type")
    except KeyError as exception:
        raise ValueError(
            "Unable to retrieve email address and token type in jwt token access token",
        ) from exception
    if email_address is None or token_type is None:
        raise ValueError(
            "Email address and token type in jwt token access token must be set",
        )

    # check provided token is an access token
    if token_type != TokenType.ACCESS:
        raise ValueError("Provided token must be an access token")

    # retrieve user in db
    user = await user_repository.get_user_by_email_address(
        email_address=email_address,
        session=session,
    )

    return UserAuthDTO(
        **user.model_dump(),
        jwt_tokens=JWTTokens(
            access_token=access_token,
            refresh_token=None,
            auth_schema="bearer",
        ),
    )


async def refresh_access_token(
    refresh_token: str,
    session: AsyncSession,
) -> UserAuthDTO:
    """
    Issues a new access token using a valid refresh token as proof of identity.

    The function validates the refresh token's authenticity and ensures it is
    not an access token. If valid, it generates a fresh access token, allowing
    the user to continue their session without re-authenticating with a password.

    :param refresh_token: The long-lived token used to renew access.
    :param session: The active asynchronous database session.
    :return: A UserAuthDTO updated with the newly generated access token.
    """
    # decode token
    try:
        payload = decode_jwt_token(
            token=refresh_token,
        )
    except JWTError as exception:
        raise ValueError(
            "Unable to decode provided jwt token access token",
        ) from exception

    # retrieve user email address in decoded token
    try:
        email_address = payload.get("sub")
        token_type = payload.get("token_type")
    except KeyError as exception:
        raise ValueError(
            "Unable to retrieve email address and token type in jwt token refresh token",
        ) from exception
    if email_address is None or token_type is None:
        raise ValueError(
            "Email address and token type in jwt token access token must be set",
        )

    # check provided token is a refresh token
    if token_type != TokenType.REFRESH:
        raise ValueError("Provided token must be a refresh token")

    # retrieve user in db
    user = await user_repository.get_user_by_email_address(
        email_address=email_address,
        session=session,
    )

    # create a new access token
    access_token_expires = timedelta(
        minutes=AUTH_SETTINGS.access_token_duration_minutes,
    )
    new_access_token = create_token(
        data={"sub": user.email_address},
        expires_delta=access_token_expires,
    )

    return UserAuthDTO(
        **user.model_dump(),
        jwt_tokens=JWTTokens(
            access_token=new_access_token,
            refresh_token=refresh_token,
            auth_schema="bearer",
        ),
    )
