from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.dtos.board_column_out_dto import BoardColumnOutDTO
from shared_models.dtos.board_event_out_dto import BoardEventOutDTO
from shared_models.dtos.user_dtos import UserOutDTO, UserWithBoardPermissionOutDTO


class BoardOutDTO(BaseModel):
    """
    Data transfer object representing the full details of a board for API output.

    :param id: Unique identifier of the board.
    :param name: Display name of the board.
    :param description: Summary text of the board.
    :param columns: List of structured columns belonging to this board.
    :param users: List of invited users with their specific board roles.
    :param events: List of milestone events linked to this board.
    :param created_by_id: ID of the user who created the board.
    :param created_by: Outbound details of the board creator.
    :param created_at: Creation date and time.
    :param updated_at: Last modification date and time.
    """

    id: UUID
    name: str | None = Field(default=None)
    description: str

    columns: list[BoardColumnOutDTO] = Field(default_factory=list)
    users: list[UserWithBoardPermissionOutDTO] = Field(default_factory=list)
    events: list[BoardEventOutDTO] = Field(default_factory=list)

    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
