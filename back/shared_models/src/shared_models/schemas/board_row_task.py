from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from ..enums import BoardTaskStatus

if TYPE_CHECKING:
    from .board_columns import BoardColumn
    from .board_row import BoardRow
    from .user import User


class BoardRowTask(SQLModel, table=True):
    __tablename__ = "board_row_tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    board_row_id: UUID = Field(foreign_key="board_rows.id", nullable=False, index=True)
    board_row: "BoardRow" = Relationship(back_populates="tasks")

    board_column_id: UUID = Field(
        foreign_key="board_columns.id",
        nullable=False,
        index=True,
    )
    board_column: "BoardColumn" = Relationship()

    task_name: str = Field(max_length=125, nullable=False)
    task_content: str = Field(default="", max_length=125, nullable=False)
    task_status: BoardTaskStatus = Field(
        default=BoardTaskStatus.PENDING,
        nullable=False,
    )
    starting_from: date = Field(default_factory=date.today, nullable=False)
    deadline: date = Field(nullable=False)

    version: int = Field(default=0, nullable=False)

    assigned_to_id: UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[BoardRowTask.assigned_to_id]"
        }
    )
    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[BoardRowTask.assigned_to_id]"
        }
    )

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
