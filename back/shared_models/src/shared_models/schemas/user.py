from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from shared_models.enums import UserRole

from .user_board_relation import UserBoardLink

if TYPE_CHECKING:
    from .board import Board


class User(SQLModel, table=True):
    """
    Represents a registered individual and primary actor within the platform.

    This model stores identity, contact, and geographic information for users
    acting as either property owners or potential tenants. It serves as the
    foundational entity for managing profiles and establishing relationships
    with housing listings and rental applications.
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email_address: str = Field(max_length=50, nullable=False, unique=True)
    password: str = Field(max_length=100, nullable=False)

    first_name: str = Field(max_length=50, nullable=False)
    last_name: str = Field(max_length=50, nullable=False)
    role: UserRole = Field(nullable=False)

    boards: list["Board"] = Relationship(
        back_populates="users", link_model=UserBoardLink,
    )

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.now),
    )
