from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.dtos.board_row_comment_out_dto import BoardRowCommentOutDTO
from shared_models.dtos.board_row_task_out_dto import BoardRowTaskOutDTO
from shared_models.dtos.user_dtos import UserOutDTO


class BoardRowOutDTO(BaseModel):
    """
    Data transfer object representing a complete horizontal row for API output.

    :param id: Unique identifier of the row.
    :param board_id: ID of the board containing this row.
    :param tasks: List of specific cellular tasks mapped inside this row.
    :param comments: List of communication comments attached to this row.
    :param created_by_id: ID of the user who created the row.
    :param created_by: Outbound details of the row creator.
    :param created_at: Creation date and time.
    :param updated_at: Last modification date and time.
    """

    id: UUID

    board_id: UUID

    tasks: list[BoardRowTaskOutDTO] = Field(default_factory=list)
    comments: list[BoardRowCommentOutDTO] = Field(default_factory=list)

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
