from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .board_columns import BoardColumn
    from .board_event import BoardEvent
    from .user import User
    from .user_board_relation import UserBoardPermission


class Board(SQLModel, table=True):
    """
    Represent a project board within the application.

    :param id: Unique identifier for the board.
    :param name: Name of the board.
    :param description: Short description of the board's purpose.
    :param columns: List of columns associated with this board.
    :param user_relations: List of user access permissions for this board.
    :param events: List of calendar events linked to this board.
    :param created_by_id: ID of the user who created the board.
    :param created_by: User instance of the board creator.
    :param created_at: Timestamp when the board was created.
    :param updated_at: Timestamp when the board was last updated.
    """

    __tablename__ = "boards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(max_length=125, nullable=True)
    description: str = Field(default="", max_length=250)

    columns: list["BoardColumn"] = Relationship(back_populates="board")
    user_relations: list["UserBoardPermission"] = Relationship(back_populates="board")
    events: list["BoardEvent"] = Relationship(back_populates="board")

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
