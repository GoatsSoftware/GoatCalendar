from asyncio import sleep
from collections.abc import AsyncGenerator

from shared_models import schemas  # noqa: F401
from shared_models.models.db_connection_settings import get_db_connection_settings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

db_conn_settings = get_db_connection_settings()
max_db_conn_retries = 10
retry_interval = 5

engine = create_async_engine(
    f"{db_conn_settings.db_dialect}://{db_conn_settings.db_url}",
    pool_size=10,
    max_overflow=20,
    pool_recycle=600,
)


async def create_db_and_tables(nb_tries: int = 0) -> None:
    """
    Initializes the database schema by creating all defined tables.

    This function uses a synchronous runner within the asynchronous
    connection to map SQLModel metadata to the SQLite file. It is
    typically called during the application startup phase.

    :return: None
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except SQLAlchemyError as exception:
        print(f"Failed to connect to db in try n°{nb_tries}, exception: {exception}")

        # retry connection
        if nb_tries < max_db_conn_retries:
            await sleep(retry_interval)
            await create_db_and_tables(nb_tries + 1)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Provides an asynchronous database session for dependency injection.

    This generator manages the lifecycle of a session, ensuring that
    the connection is opened when needed and automatically closed
    once the operation is complete.

    :yield: An active AsyncSession instance connected to the engine.
    """
    async with AsyncSession(engine) as session:
        yield session
