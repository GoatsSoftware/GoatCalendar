from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .board_row import BoardRow
    from .user import User


class BoardRowComment(SQLModel, table=True):
    """
    Represent a text comment added by a user to a specific board row.

    :param id: Unique identifier for the comment.
    :param board_row_id: ID of the row this comment is linked to.
    :param board_row: BoardRow instance associated with this comment.
    :param content: The text content of the comment.
    :param created_by_id: ID of the user who posted the comment.
    :param created_by: User instance of the comment author.
    :param created_at: Timestamp when the comment was created.
    :param updated_at: Timestamp when the comment was last updated.
    """

    __tablename__ = "board_comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_row_id: UUID = Field(foreign_key="board_rows.id", nullable=False, index=True)
    board_row: "BoardRow" = Relationship(back_populates="comments")

    content: str = Field(default="", max_length=125, nullable=False)

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
