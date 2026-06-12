from datetime import date
from uuid import UUID

from pydantic import BaseModel


class BoardEventCreateDTO(BaseModel):
    """Data to create a board event/milestone."""

    board_id: UUID
    title: str | None = None
    description: str = ""
    starting_from: date
    deadline: date


class BoardEventUpdateDTO(BaseModel):
    """Data to update a board event."""

    title: str | None = None
    description: str | None = None
    starting_from: date | None = None
    deadline: date | None = None
