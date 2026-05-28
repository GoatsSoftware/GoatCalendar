from asyncio import run

from database_service.database import create_db_and_tables, engine
from database_service.seeder import base_seeder


async def seed_db() -> None:
    """
    Executes a complete database initialization and population sequence.

    This command orchestrates the creation of the database schema followed
    by the insertion of sample records. It is intended for development and
    testing environments to ensure a consistent data state.

    :return: None
    """
    try:
        # create db and tables if not exist
        await create_db_and_tables()

        # seed db with sample data
        await base_seeder()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    run(seed_db())
