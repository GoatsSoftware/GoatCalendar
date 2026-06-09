from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.enums import BoardTaskStatus


class BoardRowTaskCreateDTO(BaseModel):
    board_row_id: UUID
    board_column_id: UUID

    task_name: str = Field(..., max_length=125)
    task_content: str = Field(default="", max_length=125)
    task_status: BoardTaskStatus = Field(default=BoardTaskStatus.PENDING)
    starting_from: date = Field(default_factory=date.today)
    deadline: date

    assigned_to_id: UUID


class BoardRowTaskUpdateDTO(BaseModel):
    task_name: Optional[str] = Field(default=None, max_length=125)
    task_content: Optional[str] = Field(default=None, max_length=125)
    task_status: Optional[BoardTaskStatus] = None
    starting_from: Optional[date] = None
    deadline: Optional[date] = None

    assigned_to_id: Optional[UUID] = None

    # Version from client for optimistic locking
    version: int
