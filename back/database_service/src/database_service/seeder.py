from datetime import date
from uuid import uuid4

from shared_models.enums import (
    BoardColumnName,
    BoardFieldType,
    BoardTaskStatus,
    UserRole,
    UserRoleInBoard,
)
from shared_models.schemas import (
    Board,
    BoardColumn,
    BoardEvent,
    BoardRow,
    BoardRowComment,
    BoardRowTask,
    User,
    UserBoardPermission,
)
from sqlmodel.ext.asyncio.session import AsyncSession

from database_service.database import engine

ALICE_EMAIL = "aliceproprio@gmail.com"
BOB_EMAIL = "boblocataire@gmail.com"
CLAIRE_EMAIL = "clairemixte@gmail.com"

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


async def seed_board_structure(session: AsyncSession, users: list[User]):
    admin, editor, viewer = users

    # 1. Board
    board = Board(
        id=uuid4(),
        name="Demo Board",
        description="Full seeded board",
        created_by_id=admin.id,
    )

    session.add(board)
    await session.flush()

    # 2. Columns (5)
    columns = []
    column_names = [
        BoardColumnName.TASK_ID,
        BoardColumnName.TASK_NAME,
        BoardColumnName.TASK_CONTENT,
        BoardColumnName.TASK_STATUS,
        BoardColumnName.DEADLINE,
    ]

    for i, name in enumerate(column_names):
        col = BoardColumn(
            id=uuid4(),
            board_id=board.id,
            name=name,
            type=BoardFieldType.TEXT,
            position=i,
            created_by_id=admin.id,
        )
        columns.append(col)

    session.add_all(columns)
    await session.flush()

    # 3. Rows + Tasks (5 rows × 5 tasks)
    rows = []
    tasks = []

    for r in range(5):
        row = BoardRow(
            id=uuid4(),
            board_id=board.id,
            created_by_id=admin.id,
        )
        session.add(row)
        await session.flush()
        rows.append(row)

        for c in range(5):
            task = BoardRowTask(
                id=uuid4(),
                board_row_id=row.id,
                board_column_id=columns[c].id,
                task_name=f"Task R{r + 1}-C{c + 1}",
                task_content=f"Content row {r + 1} column {c + 1}",
                task_status=BoardTaskStatus.PENDING,
                deadline=date.today(),
                assigned_to_id=viewer.id,
                created_by_id=admin.id,
            )
            tasks.append(task)

        # 1 comment per row
        comment = BoardRowComment(
            id=uuid4(),
            board_row_id=row.id,
            content=f"Comment for row {r + 1}",
            created_by_id=editor.id,
        )
        session.add(comment)

    session.add_all(tasks)
    await session.flush()

    # 4. Events (2)
    events = [
        BoardEvent(
            id=uuid4(),
            board_id=board.id,
            title="Kickoff",
            description="Project started",
            starting_from=board.created_at.date(),
            deadline=board.created_at.date(),
            version=1,
            created_by_id=admin.id,
        ),
        BoardEvent(
            id=uuid4(),
            board_id=board.id,
            title="Mid Review",
            description="Progress review",
            starting_from=board.created_at.date(),
            deadline=board.created_at.date(),
            version=1,
            created_by_id=editor.id,
        ),
    ]

    session.add_all(events)

    # 5. Users invited (2)
    links = [
        UserBoardPermission(
            user_id=editor.id,
            board_id=board.id,
            user_role_in_board=UserRoleInBoard.EDITOR,
        ),
        UserBoardPermission(
            user_id=viewer.id,
            board_id=board.id,
        ),
    ]

    session.add_all(links)

    await session.flush()

    return board


async def base_seeder() -> None:
    """
    Orchestrates the complete database population process in the correct order.

    This function handles the session lifecycle, manages foreign key dependencies
    between locations, users, and housings, and commits the transaction if all
    steps succeed.
    """
    async with AsyncSession(engine) as session:
        users = await seed_users(session)
        await seed_board_structure(session, users)
        await session.commit()
