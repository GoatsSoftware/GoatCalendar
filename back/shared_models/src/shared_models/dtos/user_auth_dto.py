from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared_models.models.jwt_tokens import JWTTokens


class UserAuthDTO(BaseModel):
    """
    Data transfer object packing user identity payload along with their security session tokens.

    :param id: Unique identifier of the user.
    :param email_address: Registered email login address.
    :param jwt_tokens: Object housing access and refresh JWT authorization structures.
    :param first_name: First name of the user.
    :param last_name: Last name of the user.
    """

    id: UUID
    email_address: str
    jwt_tokens: JWTTokens

    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
