from uuid import UUID

from pydantic import BaseModel


class UserOutDTO(BaseModel):
    id: UUID
    email_address: str

    first_name: str
    last_name: str
