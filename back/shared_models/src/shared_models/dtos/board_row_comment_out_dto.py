from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared_models.dtos.user_dtos import UserOutDTO


class BoardRowCommentOutDTO(BaseModel):
    """
    Data transfer object representing a row comment for API output.

    :param id: Unique identifier of the comment.
    :param board_row_id: ID of the row this comment belongs to.
    :param content: Main text content of the comment.
    :param created_by_id: ID of the user who posted the comment.
    :param created_by: Outbound details of the comment author.
    :param created_at: Creation date and time.
    :param updated_at: Last modification date and time.
    """

    id: UUID

    board_row_id: UUID

    content: str

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
