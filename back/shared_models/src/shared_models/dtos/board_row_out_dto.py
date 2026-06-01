from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.dtos.board_row_comment_out_dto import BoardRowCommentOutDTO
from shared_models.dtos.board_row_task_out_dto import BoardRowTaskOutDTO
from shared_models.dtos.user_dtos import UserOutDTO


class BoardRowOutDTO(BaseModel):
    id: UUID

    board_id: UUID

    tasks: list[BoardRowTaskOutDTO] = Field(default_factory=list)
    comments: list[BoardRowCommentOutDTO] = Field(default_factory=list)

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
