from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from ..enums import BoardTaskStatus
from .board_column_out_dto import BoardColumnOutDTO
from .user_dtos import UserOutDTO


class BoardRowTaskOutDTO(BaseModel):
    id: UUID

    board_row_id: UUID

    board_column_id: UUID
    board_column: BoardColumnOutDTO

    task_name: str
    task_content: str
    task_status: BoardTaskStatus
    starting_from: date
    deadline: date

    version: int

    assigned_to_id: UUID
    assigned_to: UserOutDTO
    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
