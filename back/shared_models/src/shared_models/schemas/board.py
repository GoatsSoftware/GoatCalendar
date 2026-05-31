from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .user_board_relation import UserBoardLink

if TYPE_CHECKING:
    from .board_columns import BoardColumn
    from .board_event import BoardEvent
    from .user import User


class Board(SQLModel, table=True):
    __tablename__ = "boards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(max_length=125, nullable=True)
    description: str = Field(default="", max_length=250)

    columns: list["BoardColumn"] = Relationship(back_populates="board")
    users: list["User"] = Relationship(
        back_populates="boards", link_model=UserBoardLink,
    )
    events: list["BoardEvent"] = Relationship(back_populates="board")

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
