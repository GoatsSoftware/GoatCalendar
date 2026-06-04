from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .board import Board
    from .user import User


class BoardEvent(SQLModel, table=True):
    """
    Represent a timeline event or milestone linked to a board.

    :param id: Unique identifier for the event.
    :param board_id: ID of the board this event belongs to.
    :param board: Board instance associated with this event.
    :param title: Title of the event.
    :param description: Detailed description of the event.
    :param starting_from: Start date of the event.
    :param deadline: End or target date for the event.
    :param version: Optimistic locking version number.
    :param created_by_id: ID of the user who created the event.
    :param created_by: User instance of the event creator.
    :param created_at: Timestamp when the event was created.
    :param updated_at: Timestamp when the event was last updated.
    """

    __tablename__ = "board_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_id: UUID = Field(foreign_key="boards.id", nullable=False, index=True)
    board: "Board" = Relationship(back_populates="events")

    title: str = Field(max_length=125, nullable=True)
    description: str = Field(default="", max_length=250)
    starting_from: date = Field(default_factory=date.today, nullable=False)
    deadline: date = Field(nullable=False)

    version: int = Field(default=0, nullable=False)

    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
