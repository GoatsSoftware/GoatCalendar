from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BoardEventCreateDTO(BaseModel):
    """Data to create a board event/milestone."""

    board_id: UUID
    title: Optional[str] = None
    description: str = ""
    starting_from: date
    deadline: date


class BoardEventUpdateDTO(BaseModel):
    """Data to update a board event."""

    title: Optional[str] = None
    description: Optional[str] = None
    starting_from: Optional[date] = None
    deadline: Optional[date] = None
