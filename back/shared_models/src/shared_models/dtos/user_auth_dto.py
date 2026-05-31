from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared_models.models.jwt_tokens import JWTTokens


class UserAuthDTO(BaseModel):
    id: UUID
    email_address: str
    jwt_tokens: JWTTokens

    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
