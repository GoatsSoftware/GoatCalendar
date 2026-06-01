from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.dtos.board_column_out_dto import BoardColumnOutDTO
from shared_models.dtos.user_dtos import UserOutDTO, UserWithBoardPermissionOutDTO
from shared_models.schemas import BoardEvent


class BoardOutDTO(BaseModel):
    id: UUID
    name: str | None = Field(default=None)
    description: str

    columns: list[BoardColumnOutDTO] = Field(default_factory=list)
    users: list[UserWithBoardPermissionOutDTO] = Field(default_factory=list)
    events: list[BoardEvent] = Field(default_factory=list)

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
