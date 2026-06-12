from uuid import UUID

from pydantic import BaseModel

from shared_models.enums import UserRoleInBoard

from .user_dtos import UserOutDTO


class BoardPermissionOutDTO(BaseModel):
    """Serialized board permission for API responses."""

    user_id: UUID
    board_id: UUID
    user_role_in_board: UserRoleInBoard
    user: UserOutDTO
