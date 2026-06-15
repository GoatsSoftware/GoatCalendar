from datetime import timedelta
from unittest.mock import patch

from shared_models.enums import TokenType

from auth_service.utils.hash import compare_text_with_hash, hash_str_chain
from auth_service.utils.jwt import create_token, decode_jwt_token
from tests.constants import EMAIL


class TestHashUtils:
    def test_hash_and_compare(self) -> None:
        hashed = hash_str_chain("password")

        assert hashed != "password"
        assert compare_text_with_hash("password", hashed)
        assert not compare_text_with_hash("wrong", hashed)
        assert not compare_text_with_hash("password", "invalid-hash")


class TestJwtUtils:
    def test_create_and_decode_token(self) -> None:
        token = create_token(
            {"sub": EMAIL, "token_type": TokenType.ACCESS},
            timedelta(minutes=5),
        )

        payload = decode_jwt_token(token)

        assert payload["sub"] == EMAIL
        assert payload["token_type"] == TokenType.ACCESS
        assert "exp" in payload

    def test_decode_delegates_to_jose(self) -> None:
        with patch(
            "auth_service.utils.jwt.jwt.decode",
            return_value={"sub": EMAIL},
        ) as decode_mock:
            result = decode_jwt_token("token")

        assert result == {"sub": EMAIL}
        decode_mock.assert_called_once()
