from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from .user_dtos import UserOutDTO


class BoardEventOutDTO(BaseModel):
    """Serialized board event for API responses."""

    id: UUID

    board_id: UUID

    title: str | None
    description: str
    starting_from: date
    deadline: date

    version: int

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
