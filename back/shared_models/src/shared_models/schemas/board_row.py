from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .board import Board
    from .board_row_comment import BoardRowComment
    from .board_row_task import BoardRowTask
    from .user import User


class BoardRow(SQLModel, table=True):
    """
    Represent a horizontal row containing tasks within a project board.

    :param id: Unique identifier for the row.
    :param board_id: ID of the board this row belongs to.
    :param board: Board instance associated with this row.
    :param tasks: List of tasks contained within this row.
    :param comments: List of comments attached to this row.
    :param created_by_id: ID of the user who created the row.
    :param created_by: User instance of the row creator.
    :param created_at: Timestamp when the row was created.
    :param updated_at: Timestamp when the row was last updated.
    """

    __tablename__ = "board_rows"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_id: UUID = Field(foreign_key="boards.id", nullable=False, index=True)
    board: "Board" = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    tasks: list["BoardRowTask"] = Relationship(back_populates="board_row")
    comments: list["BoardRowComment"] = Relationship(back_populates="board_row")

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
