import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from shared_models.dtos.user_dtos import UserInDTO
from shared_models.enums import TokenType
from shared_models.schemas import User

from auth_service.services import authentication_service, user_service
from tests.constants import EMAIL, USER_ID


class TestAuthenticationService:
    def test_login(self, user: User) -> None:
        credentials = OAuth2PasswordRequestForm(
            username=EMAIL,
            password="password",
            scope="",
            client_id=None,
            client_secret=None,
        )
        session = Mock()

        with (
            patch.object(
                authentication_service.user_repository,
                "get_user_by_email_address",
                new=AsyncMock(return_value=user),
            ),
            patch.object(
                authentication_service,
                "compare_text_with_hash",
                return_value=True,
            ),
            patch.object(
                authentication_service,
                "create_token",
                side_effect=["access-token", "refresh-token"],
            ) as create_token_mock,
        ):
            result = asyncio.run(authentication_service.login(credentials, session))

        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert create_token_mock.call_count == 2

    def test_login_with_invalid_password(self, user: User) -> None:
        credentials = OAuth2PasswordRequestForm(
            username=EMAIL,
            password="wrong",
            scope="",
            client_id=None,
            client_secret=None,
        )

        with (
            patch.object(
                authentication_service.user_repository,
                "get_user_by_email_address",
                new=AsyncMock(return_value=user),
            ),
            patch.object(
                authentication_service,
                "compare_text_with_hash",
                return_value=False,
            ),
            pytest.raises(ValueError, match="does not match"),
        ):
            asyncio.run(authentication_service.login(credentials, Mock()))

    def test_check_auth_user(self, user: User) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                return_value={"sub": EMAIL, "token_type": TokenType.ACCESS},
            ),
            patch.object(
                authentication_service.user_repository,
                "get_user_by_email_address",
                new=AsyncMock(return_value=user),
            ),
        ):
            result = asyncio.run(
                authentication_service.check_auth_user("access-token", Mock()),
            )

        assert result.id == USER_ID
        assert result.jwt_tokens.access_token == "access-token"

    @pytest.mark.parametrize(
        ("payload", "message"),
        [
            ({}, "must be set"),
            (
                {"sub": EMAIL, "token_type": TokenType.REFRESH},
                "must be an access token",
            ),
        ],
    )
    def test_check_auth_user_rejects_invalid_payload(
        self,
        payload: dict,
        message: str,
    ) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                return_value=payload,
            ),
            pytest.raises(ValueError, match=message),
        ):
            asyncio.run(
                authentication_service.check_auth_user("access-token", Mock()),
            )

    def test_check_auth_user_rejects_invalid_jwt(self) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                side_effect=JWTError,
            ),
            pytest.raises(ValueError, match="Unable to decode"),
        ):
            asyncio.run(
                authentication_service.check_auth_user("access-token", Mock()),
            )

    def test_refresh_access_token(self, user: User) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                return_value={"sub": EMAIL, "token_type": TokenType.REFRESH},
            ),
            patch.object(
                authentication_service.user_repository,
                "get_user_by_email_address",
                new=AsyncMock(return_value=user),
            ),
            patch.object(
                authentication_service,
                "create_token",
                return_value="new-access-token",
            ) as create_token_mock,
        ):
            result = asyncio.run(
                authentication_service.refresh_access_token(
                    "refresh-token",
                    Mock(),
                ),
            )

        assert result.jwt_tokens.access_token == "new-access-token"
        assert result.jwt_tokens.refresh_token == "refresh-token"
        assert create_token_mock.call_args.kwargs["data"] == {
            "sub": EMAIL,
            "token_type": TokenType.ACCESS,
        }

    @pytest.mark.parametrize(
        ("payload", "message"),
        [
            ({}, "must be set"),
            (
                {"sub": EMAIL, "token_type": TokenType.ACCESS},
                "must be a refresh token",
            ),
        ],
    )
    def test_refresh_rejects_invalid_payload(
        self,
        payload: dict,
        message: str,
    ) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                return_value=payload,
            ),
            pytest.raises(ValueError, match=message),
        ):
            asyncio.run(
                authentication_service.refresh_access_token("refresh-token", Mock()),
            )

    def test_refresh_rejects_invalid_jwt(self) -> None:
        with (
            patch.object(
                authentication_service,
                "decode_jwt_token",
                side_effect=JWTError,
            ),
            pytest.raises(ValueError, match="Unable to decode"),
        ):
            asyncio.run(
                authentication_service.refresh_access_token("refresh-token", Mock()),
            )


class TestUserService:
    def test_user_service_delegates(self, user: User) -> None:
        session = Mock()
        update_data = UserInDTO(first_name="Updated")

        with (
            patch.object(
                user_service.user_repository,
                "get_all_users",
                new=AsyncMock(return_value=[user]),
            ) as get_all_mock,
            patch.object(
                user_service.user_repository,
                "search_users",
                new=AsyncMock(return_value=[user]),
            ) as search_mock,
            patch.object(
                user_service.user_repository,
                "update_user",
                new=AsyncMock(return_value=user),
            ) as update_mock,
        ):
            assert asyncio.run(user_service.get_all_users(session)) == [user]
            assert asyncio.run(user_service.search_users("test", session)) == [user]
            assert (
                asyncio.run(user_service.update_user(USER_ID, update_data, session))
                is user
            )

        get_all_mock.assert_awaited_once_with(session)
        search_mock.assert_awaited_once_with("test", session)
        update_mock.assert_awaited_once_with(USER_ID, update_data, session)
