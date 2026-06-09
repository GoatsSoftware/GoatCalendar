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


async def search_users(query: str, session: AsyncSession) -> list[User]:
    """Search users by display name or email."""
    from sqlalchemy import or_
    search_term = f"%{query}%"
    statement = select(User).where(
        or_(
            User.display_name.ilike(search_term),
            User.email_address.ilike(search_term),
        )
    )
    result = await session.exec(statement)
    return result.unique().all()


async def update_user(user_id, update_data: dict, session: AsyncSession) -> User:
    """Update a user record."""
    from sqlalchemy.exc import NoResultFound
    from uuid import UUID
    user = await session.get(User, user_id)
    if user is None:
        raise NoResultFound
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
