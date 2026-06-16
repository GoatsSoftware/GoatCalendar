from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.enums import BoardTaskStatus


class BoardRowTaskCreateDTO(BaseModel):
    """Payload used to create a task in a board row."""

    board_row_id: UUID
    board_column_id: UUID

    task_name: str = Field(..., max_length=125)
    task_content: str = Field(default="", max_length=125)
    task_status: BoardTaskStatus = Field(default=BoardTaskStatus.PENDING)
    starting_from: date = Field(default_factory=date.today)
    deadline: date

    assigned_to_id: UUID


class BoardRowTaskUpdateDTO(BaseModel):
    """Payload used to update a task in a board row."""

    task_name: str | None = Field(default=None, max_length=125)
    task_content: str | None = Field(default=None, max_length=125)
    task_status: BoardTaskStatus | None = None
    starting_from: date | None = None
    deadline: date | None = None

    assigned_to_id: UUID | None = None

    # Version from client for optimistic locking
    version: int
