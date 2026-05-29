from uuid import UUID

from sqlmodel import Field, SQLModel

from shared_models.enums import UserRoleInBoard


class UserBoardLink(SQLModel, table=True):
    __tablename__ = "users_boards_link"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    board_id: UUID = Field(foreign_key="boards.id", primary_key=True)
    user_role_in_board: UserRoleInBoard = Field(
        default=UserRoleInBoard.VIEWER,
        nullable=False,
    )
