from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from shared_models.models.auth_settings import get_auth_settings

ALGORITHM = "HS512"
AUTH_SETTINGS = get_auth_settings()


def create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Generates an encrypted and signed JSON Web Token.

    This function accepts a data payload, injects a UTC expiration
    timestamp, and signs the resulting dictionary using a secure
    server-side key. The resulting string can be safely shared
    with clients for authentication purposes.

    :param data: The claim dictionary to be encoded into the token.
    :param expires_delta: The duration for which the token remains valid.
    :return: A base64-encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH_SETTINGS.encryption_key, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict[str, Any]:
    """
    Validates a JWT string and extracts its original payload.

    This function verifies the token's cryptographic signature against
    the server's secret key and checks the expiration claim. If the
    token is authentic and valid, it returns the decoded data.

    :param token: The encoded JWT string received from a client.
    :return: The original dictionary containing the token claims.
    """
    return jwt.decode(token, AUTH_SETTINGS.encryption_key, algorithms=[ALGORITHM])
