from shared_models.schemas import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_all_users(session: AsyncSession) -> list[User]:
    statement = select(User)

    result = await session.exec(statement)
    return result.unique().all()
