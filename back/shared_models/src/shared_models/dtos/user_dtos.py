from uuid import UUID

from pydantic import BaseModel, Field

from shared_models.enums import UserRoleInBoard


class UserOutDTO(BaseModel):
    """
    Data transfer object providing safe, standard public user details for API output.

    :param id: Unique identifier of the user.
    :param email_address: Public contact or identity email address.
    :param first_name: First name of the user.
    :param last_name: Last name of the user.
    """

    id: UUID
    email_address: str

    first_name: str
    last_name: str


class UserInDTO(BaseModel):
    """Input payload used to create or update a user."""

    email_address: str | None = Field(default=None)

    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)


class UserWithBoardPermissionOutDTO(UserOutDTO):
    """
    Data transfer object extending public user details with contextual structural board permissions.

    :param user_role_in_board: Explicit contextual role level held by this user inside the board.
    """

    user_role_in_board: UserRoleInBoard
