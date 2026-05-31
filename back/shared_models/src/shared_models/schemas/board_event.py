from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .user import User

if TYPE_CHECKING:
    from .board import Board


class BoardEvent(SQLModel, table=True):
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
    created_by: User = Relationship()

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
