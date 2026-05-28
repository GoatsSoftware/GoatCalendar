from uuid import uuid4

from shared_models.enums import UserRole
from shared_models.schemas.user import User
from sqlmodel.ext.asyncio.session import AsyncSession

from database_service.database import engine

ALICE_EMAIL = "aliceproprio@gmail.com"
BOB_EMAIL = "boblocataire@gmail.com"
CLAIRE_EMAIL = "clairemixte@gmail.com"

ADDRESS_RIVOLI = "25 Rue de Rivoli"
ADDRESS_MEDOC = "7 Cours du Medoc"
ADDRESS_KERVEGAN = "12 Rue Kervegan"
ADDRESS_SAINT_FERREOL = "14 Rue Saint-Ferreol"

DEFAULT_USER_HASH = "$argon2id$v=19$m=65536,t=3,p=4$xVhr7Z3z3hsjxJiTcm5tzQ$unBxBAVRdz9Oaa3ByFIhxXNF28zIwfQlNp0E9om+9ow"


async def seed_users(session: AsyncSession) -> list[User]:
    """
    Creates and persists a set of initial users in the database.

    :param session: The active asynchronous database session.
    :return: A list of newly created User instances.
    """
    users = [
        User(
            id=uuid4(),
            email_address=ALICE_EMAIL,
            password=DEFAULT_USER_HASH,
            first_name="Alice",
            last_name="Proprio",
            role=UserRole.ADMIN,
        ),
        User(
            id=uuid4(),
            email_address=BOB_EMAIL,
            password=DEFAULT_USER_HASH,
            first_name="Bob",
            last_name="Locataire",
            role=UserRole.USER,
        ),
        User(
            id=uuid4(),
            email_address=CLAIRE_EMAIL,
            password=DEFAULT_USER_HASH,
            first_name="Claire",
            last_name="Mixte",
            role=UserRole.USER,
        ),
    ]

    session.add_all(users)
    await session.flush()

    return users


async def base_seeder() -> None:
    """
    Orchestrates the complete database population process in the correct order.

    This function handles the session lifecycle, manages foreign key dependencies
    between locations, users, and housings, and commits the transaction if all
    steps succeed.
    """
    async with AsyncSession(engine) as session:
        await seed_users(session)
        await session.commit()
