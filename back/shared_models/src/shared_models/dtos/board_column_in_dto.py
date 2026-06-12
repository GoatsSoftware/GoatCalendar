from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.enums import BoardColumnName, BoardFieldType


class BoardColumnCreateDTO(BaseModel):
    """Data to create a new board column."""

    board_id: UUID
    name: BoardColumnName
    type: BoardFieldType = Field(default=BoardFieldType.TEXT)
    position: int = Field(ge=0)


class BoardColumnUpdateDTO(BaseModel):
    """Data to update a board column."""

    name: BoardColumnName | None = None
    type: BoardFieldType | None = None
    position: int | None = Field(default=None, ge=0)
