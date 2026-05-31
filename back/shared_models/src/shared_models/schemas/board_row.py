from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .user import User

if TYPE_CHECKING:
    from .board import Board
    from .board_row_comment import BoardRowComment
    from .board_row_task import BoardRowTask


class BoardRow(SQLModel, table=True):
    __tablename__ = "board_rows"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_id: UUID = Field(foreign_key="boards.id", nullable=False, index=True)
    board: "Board" = Relationship(    sa_relationship_kwargs={"lazy": "selectin"})

    tasks: list["BoardRowTask"] = Relationship(back_populates="board_row")
    comments: list["BoardRowComment"] = Relationship(back_populates="board_row")

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: User = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
