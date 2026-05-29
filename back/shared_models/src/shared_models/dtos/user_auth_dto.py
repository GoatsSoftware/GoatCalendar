from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared_models.models.jwt_tokens import JWTTokens


class UserAuthDTO(BaseModel):
    """
    Combines core user identity with active session security tokens.

    This comprehensive data transfer object is returned upon successful
    authentication or token refresh. It bundles the user's personal
    profile and the JWT credentials required for subsequent authorized requests.
    """

    id: UUID
    email_address: str
    jwt_tokens: JWTTokens

    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
