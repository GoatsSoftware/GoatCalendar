from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .user import User

if TYPE_CHECKING:
    from .board_row import BoardRow


class BoardRowComment(SQLModel, table=True):
    __tablename__ = "board_comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_row_id: UUID = Field(foreign_key="board_rows.id", nullable=False, index=True)
    board_row: "BoardRow" = Relationship(back_populates="comments")

    content: str = Field(default="", max_length=125, nullable=False)

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: User = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
