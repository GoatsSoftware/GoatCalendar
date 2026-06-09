from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from shared_models.enums import BoardTaskStatus

if TYPE_CHECKING:
    from .board_columns import BoardColumn
    from .board_row import BoardRow
    from .user import User


class BoardRowTask(SQLModel, table=True):
    """
    Represent an individual task located at the intersection of a row and a column.

    :param id: Unique identifier for the task.
    :param board_row_id: ID of the row this task belongs to.
    :param board_row: BoardRow instance associated with this task.
    :param board_column_id: ID of the column this task belongs to.
    :param board_column: BoardColumn instance associated with this task.
    :param task_name: Summary name of the task.
    :param task_content: Main text details or description of the task.
    :param task_status: Current lifecycle status of the task.
    :param starting_from: Date when work on the task should begin.
    :param deadline: Due date for completing the task.
    :param version: Optimistic locking version number.
    :param assigned_to_id: ID of the user assigned to complete the task.
    :param assigned_to: User instance of the assignee.
    :param created_by_id: ID of the user who created the task.
    :param created_by: User instance of the task creator.
    :param created_at: Timestamp when the task was created.
    :param updated_at: Timestamp when the task was last updated.
    """

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

    version: int = Field(default=1, nullable=False)

    assigned_to_id: UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoardRowTask.assigned_to_id]"},
    )
    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoardRowTask.created_by_id]"},
    )

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
