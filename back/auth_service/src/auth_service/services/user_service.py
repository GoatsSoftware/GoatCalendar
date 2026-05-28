from shared_models.schemas import User
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.repositories import user_repository


async def get_all_users(session: AsyncSession) -> list[User]:
    return await user_repository.get_all_users(session)
