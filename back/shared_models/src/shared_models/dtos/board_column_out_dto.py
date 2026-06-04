from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared_models.enums import BoardColumnName, BoardFieldType

from .user_dtos import UserOutDTO


class BoardColumnOutDTO(BaseModel):
    """
    Data transfer object representing a serialized board column for API output.

    :param id: Unique identifier of the column.
    :param board_id: ID of the board this column belongs to.
    :param name: Functional name of the column.
    :param type: Data formatting type of the column.
    :param position: Visual ordering index of the column.
    :param created_by_id: ID of the user who created the column.
    :param created_by: Outbound details of the column creator.
    :param created_at: Creation date and time.
    :param updated_at: Last modification date and time.
    """

    id: UUID

    board_id: UUID

    name: BoardColumnName
    type: BoardFieldType
    position: int

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
