from pydantic import BaseModel, field_validator

MIN_SEARCH_QUERY_LENGTH = 2


class UserSearchQueryDTO(BaseModel):
    """Validated query params for user search endpoint."""

    q: str

    @field_validator("q")
    @classmethod
    def validate_q(cls, value: str) -> str:
        """Reject search queries containing unsupported characters."""  # noqa: D202

        normalized_value = value.strip()
        message = f"Search query must be at least {MIN_SEARCH_QUERY_LENGTH} characters"

        if len(normalized_value) < MIN_SEARCH_QUERY_LENGTH:
            raise ValueError(message)

        return normalized_value
