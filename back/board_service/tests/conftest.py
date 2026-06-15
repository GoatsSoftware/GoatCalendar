import os
from collections.abc import Iterator
from unittest.mock import Mock

import pytest

os.environ.setdefault("FRONT_URL", "http://testserver")
os.environ.setdefault("ENV_MODE", "dev")
os.environ.setdefault("DB_DIALECT", "mysql+aiomysql")
os.environ.setdefault("DB_URL", "user:password@localhost:3306/test")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key")
os.environ.setdefault("ACCESS_TOKEN_DURATION_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_DURATION_HOURS", "24")

from auth_service.routes.authentication_route import get_current_user
from database_service.database import get_db_session
from fastapi.testclient import TestClient
from shared_models.dtos.board_out_dto import BoardOutDTO
from shared_models.dtos.board_row_out_dto import BoardRowOutDTO
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.dtos.user_dtos import UserOutDTO
from shared_models.models.jwt_tokens import JWTTokens
from sqlalchemy.ext.asyncio.session import AsyncSession

from main import app
from tests.constants import BOARD_ID, BOARD_ROW_ID, NOW, USER_ID


@pytest.fixture
def user() -> UserOutDTO:
    return UserOutDTO(
        id=USER_ID,
        email_address="test@example.com",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def current_user() -> UserAuthDTO:
    return UserAuthDTO(
        id=USER_ID,
        email_address="test@example.com",
        first_name="Test",
        last_name="User",
        jwt_tokens=JWTTokens(
            access_token="access-token",
            refresh_token="refresh-token",
            auth_schema="bearer",
        ),
    )


@pytest.fixture
def board(user: UserOutDTO) -> BoardOutDTO:
    return BoardOutDTO(
        id=BOARD_ID,
        name="Test board",
        description="Board used by tests",
        created_by_id=USER_ID,
        created_by=user,
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.fixture
def board_row(user: UserOutDTO) -> BoardRowOutDTO:
    return BoardRowOutDTO(
        id=BOARD_ROW_ID,
        board_id=BOARD_ID,
        created_by_id=USER_ID,
        created_by=user,
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.fixture
def session() -> Mock:
    return Mock(spec=AsyncSession)


@pytest.fixture
def client(current_user: UserAuthDTO, session: Mock) -> Iterator[TestClient]:
    async def override_current_user() -> UserAuthDTO:
        return current_user

    async def override_db_session() -> Mock:
        return session

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
