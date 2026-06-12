from uuid import UUID

from shared_models.dtos.user_dtos import UserInDTO
from shared_models.schemas import User
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.repositories import user_repository


async def get_all_users(session: AsyncSession) -> list[User]:
    """
    Retrieve all registered users from the database via the repository layer.

    :param session: The active asynchronous database session.
    :return: A list of all User instances.
    """
    return await user_repository.get_all_users(session)


async def search_users(query: str, session: AsyncSession) -> list[User]:
    """Search users by name or email."""
    return await user_repository.search_users(query, session)


async def update_user(
    user_id: UUID,
    update_data: UserInDTO,
    session: AsyncSession,
) -> User:
    """Update a user's profile."""
    return await user_repository.update_user(user_id, update_data, session)
