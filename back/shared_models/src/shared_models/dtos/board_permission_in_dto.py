from uuid import UUID

from pydantic import BaseModel

from shared_models.enums import UserRoleInBoard


class BoardPermissionCreateDTO(BaseModel):
    """Data to add a user to a board."""

    user_id: UUID
    user_role_in_board: UserRoleInBoard = UserRoleInBoard.VIEWER


class BoardPermissionUpdateDTO(BaseModel):
    """Data to update a user's board role."""

    user_role_in_board: UserRoleInBoard
