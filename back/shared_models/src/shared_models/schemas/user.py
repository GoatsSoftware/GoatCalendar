from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from shared_models.enums import UserRole


class User(SQLModel, table=True):
    """
    Represents a registered individual and primary actor within the platform.

    This model stores identity, contact, and geographic information for users
    acting as either property owners or potential tenants. It serves as the
    foundational entity for managing profiles and establishing relationships
    with housing listings and rental applications.
    """

    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email_address: str = Field(max_length=50, nullable=False, unique=True)
    password: str = Field(max_length=100, nullable=False)
    first_name: str = Field(max_length=50, nullable=False)
    last_name: str = Field(max_length=50, nullable=False)
    role: UserRole = Field(nullable=False)
