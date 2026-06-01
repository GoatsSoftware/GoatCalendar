from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from shared_models.enums import UserRoleInBoard

if TYPE_CHECKING:
    from .board import Board
    from .user import User


class UserBoardPermission(SQLModel, table=True):
    __tablename__ = "users_boards_permission"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    board_id: UUID = Field(foreign_key="boards.id", primary_key=True)
    user_role_in_board: UserRoleInBoard = Field(
        default=UserRoleInBoard.VIEWER,
        nullable=False,
    )

    user: "User" = Relationship(back_populates="board_relations")
    board: "Board" = Relationship(back_populates="user_relations")
