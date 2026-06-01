from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from ..enums import BoardColumnName, BoardFieldType
from .user_dtos import UserOutDTO


class BoardColumnOutDTO(BaseModel):
    id: UUID

    board_id: UUID

    name: BoardColumnName
    type: BoardFieldType
    position: int

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
