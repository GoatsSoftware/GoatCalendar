import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from shared_models.dtos.user_auth_dto import UserAuthDTO
from shared_models.models.jwt_tokens import JWTTokens
from shared_models.schemas import User
from sqlalchemy.exc import NoResultFound

from auth_service.routes import authentication_route
from tests.constants import EMAIL


class TestAuthenticationRoutes:
    def test_get_current_user_requires_token(self) -> None:
        with pytest.raises(HTTPException) as exception:
            asyncio.run(authentication_route.get_current_user(Mock(), None))

        assert exception.value.status_code == 401

    def test_get_current_user(self, current_user: UserAuthDTO) -> None:
        with patch.object(
            authentication_route,
            "check_auth_user",
            new=AsyncMock(return_value=current_user),
        ):
            result = asyncio.run(
                authentication_route.get_current_user(Mock(), "access-token"),
            )

        assert result == current_user

    @pytest.mark.parametrize("error", [NoResultFound(), ValueError()])
    def test_get_current_user_rejects_invalid_credentials(
        self, error: Exception
    ) -> None:
        with (
            patch.object(
                authentication_route,
                "check_auth_user",
                new=AsyncMock(side_effect=error),
            ),
            pytest.raises(HTTPException) as exception,
        ):
            asyncio.run(
                authentication_route.get_current_user(Mock(), "access-token"),
            )

        assert exception.value.status_code == 401

    def test_authenticate_user(self, client: TestClient) -> None:
        tokens = JWTTokens(
            access_token="access-token",
            refresh_token="refresh-token",
            auth_schema="bearer",
        )
        with patch.object(
            authentication_route,
            "login",
            new=AsyncMock(return_value=tokens),
        ):
            response = client.post(
                "/authentication/auth",
                data={"username": EMAIL, "password": "password"},
            )

        assert response.status_code == 201
        assert response.json() == tokens.model_dump(mode="json")

    def test_authenticate_user_rejects_credentials(self, client: TestClient) -> None:
        with patch.object(
            authentication_route,
            "login",
            new=AsyncMock(side_effect=ValueError),
        ):
            response = client.post(
                "/authentication/auth",
                data={"username": EMAIL, "password": "wrong"},
            )

        assert response.status_code == 401

    def test_refresh_access_token(
        self,
        client: TestClient,
        current_user: UserAuthDTO,
    ) -> None:
        with patch.object(
            authentication_route,
            "refresh_access_token",
            new=AsyncMock(return_value=current_user),
        ):
            response = client.post(
                "/authentication/refresh-access-token",
                params={"refresh_token": "refresh-token"},
            )

        assert response.status_code == 201
        assert response.json() == current_user.model_dump(mode="json")

    def test_me(self, client: TestClient, current_user: UserAuthDTO) -> None:
        response = client.get("/authentication/me")

        assert response.status_code == 200
        assert response.json() == current_user.model_dump(mode="json")


class TestUserRoutes:
    def test_get_all_users(self, client: TestClient, user: User) -> None:
        with patch(
            "auth_service.services.user_service.get_all_users",
            new=AsyncMock(return_value=[user]),
        ):
            response = client.get("/users")

        assert response.status_code == 200
        assert response.json()[0]["email_address"] == EMAIL

    def test_search_users(self, client: TestClient, user: User) -> None:
        with patch(
            "auth_service.services.user_service.search_users",
            new=AsyncMock(return_value=[user]),
        ):
            response = client.get("/users/search", params={"q": "test"})

        assert response.status_code == 200
        assert response.json()[0]["email_address"] == EMAIL

    def test_update_me(self, client: TestClient, user: User) -> None:
        with patch(
            "auth_service.services.user_service.update_user",
            new=AsyncMock(return_value=user),
        ):
            response = client.put("/users/me", json={"first_name": "Updated"})

        assert response.status_code == 200

    def test_update_me_not_found(self, client: TestClient) -> None:
        with patch(
            "auth_service.services.user_service.update_user",
            new=AsyncMock(side_effect=NoResultFound),
        ):
            response = client.put("/users/me", json={"first_name": "Updated"})

        assert response.status_code == 404

    def test_update_me_invalid(self, client: TestClient) -> None:
        with patch(
            "auth_service.services.user_service.update_user",
            new=AsyncMock(side_effect=RuntimeError("Invalid update")),
        ):
            response = client.put("/users/me", json={"first_name": "Updated"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid update"}

    def test_health(self, client: TestClient) -> None:
        response = client.get("/auth_monitoring/health")

        assert response.status_code == 200
        assert response.json() == {
            "service_name": "Auth Service",
            "status": "up",
        }
