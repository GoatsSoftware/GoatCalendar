from uuid import UUID

from pydantic import BaseModel

from shared_models.enums import UserRoleInBoard


class UserOutDTO(BaseModel):
    id: UUID
    email_address: str

    first_name: str
    last_name: str


class UserWithBoardPermissionOutDTO(UserOutDTO):
    user_role_in_board: UserRoleInBoard
