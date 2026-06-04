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
