from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared_models.dtos.user_out_dto import UserOutDTO


class BoardRowCommentOutDTO(BaseModel):
    id: UUID

    board_row_id: UUID

    content: str

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
