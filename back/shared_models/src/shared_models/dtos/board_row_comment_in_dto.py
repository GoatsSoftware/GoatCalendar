from uuid import UUID

from pydantic import BaseModel, Field


class BoardRowCommentCreateDTO(BaseModel):
    """Data to create a comment on a board row."""

    board_row_id: UUID
    content: str = Field(..., max_length=125)


class BoardRowCommentUpdateDTO(BaseModel):
    """Data to update a board row comment."""

    content: str | None = Field(default=None, max_length=125)
