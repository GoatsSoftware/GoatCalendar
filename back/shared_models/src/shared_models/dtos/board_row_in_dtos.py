from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BoardRowCreateDTO(BaseModel):
    """Data required to create a new board row."""

    board_id: UUID


class BoardRowUpdateDTO(BaseModel):
    """Fields accepted when updating an existing board row."""

    board_id: Optional[UUID] = None
