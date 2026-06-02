from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from shared_models.enums import UserRoleInBoard

if TYPE_CHECKING:
    from .board import Board
    from .user import User


class UserBoardPermission(SQLModel, table=True):
    """
    Pivot table managing a user's role and permissions inside a specific board.

    :param user_id: ID of the member user.
    :param board_id: ID of the target board.
    :param user_role_in_board: Specific access level role of the user on this board.
    :param user: User instance linked to this permission.
    :param board: Board instance linked to this permission.
    """

    __tablename__ = "users_boards_permission"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    board_id: UUID = Field(foreign_key="boards.id", primary_key=True)
    user_role_in_board: UserRoleInBoard = Field(
        default=UserRoleInBoard.VIEWER,
        nullable=False,
    )

    user: "User" = Relationship(back_populates="board_relations")
    board: "Board" = Relationship(back_populates="user_relations")
