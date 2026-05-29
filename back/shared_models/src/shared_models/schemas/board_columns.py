from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from ..enums import BoardColumnName, BoardFieldType

if TYPE_CHECKING:
    from .board import Board
    from .user import User


class BoardColumn(SQLModel, table=True):
    __tablename__ = "board_columns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_id: UUID = Field(foreign_key="boards.id", nullable=False, index=True)
    board: "Board" = Relationship(back_populates="columns")

    name: BoardColumnName = Field(nullable=False)
    type: BoardFieldType = Field(default=BoardFieldType.TEXT, nullable=False)
    position: int = Field(ge=0)

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
