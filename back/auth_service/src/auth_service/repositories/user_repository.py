from shared_models.schemas import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_all_users(session: AsyncSession) -> list[User]:
    """
    Fetch all users from the database.

    :param session: The active asynchronous database session.
    :return: A list of all unique User records.
    """
    statement = select(User)

    result = await session.exec(statement)
    return result.unique().all()


async def get_user_by_email_address(email_address: str, session: AsyncSession) -> User:
    """
    Retrieves a user profile using a specific email address.

    This function is commonly used for authentication and profile
    lookups, ensuring that the linked location data is loaded
    alongside the user's personal details.

    :param email_address: The unique email string associated with the account.
    :param session: The active asynchronous database session.
    :return: The User instance associated with the given email address.
    """
    statement = select(User).where(User.email_address == email_address)
    result = await session.exec(statement)
    return result.unique().one()
