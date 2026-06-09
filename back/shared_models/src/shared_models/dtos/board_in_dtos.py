from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BoardCreateDTO(BaseModel):
    """Data required to create a new board."""

    name: str = Field(..., max_length=125)
    description: str = Field(default="", max_length=250)


class BoardUpdateDTO(BaseModel):
    """Fields accepted when updating an existing board."""

    name: Optional[str] = Field(default=None, max_length=125)
    description: Optional[str] = Field(default=None, max_length=250)
