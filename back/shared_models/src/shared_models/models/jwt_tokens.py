from pydantic import BaseModel, ConfigDict, Field


class JWTTokens(BaseModel):
    """
    Encapsulates the security credentials issued to a client.

    This model serves as the standard container for transporting JSON Web
    Tokens between the identity provider and consumers. It facilitates
    the implementation of the OAuth2 Bearer token flow by bundling the
    access credential with an optional renewal token and the
    specified authentication schema.
    """

    access_token: str
    refresh_token: str | None = Field(default=None)
    auth_schema: str

    model_config = ConfigDict(from_attributes=True)
