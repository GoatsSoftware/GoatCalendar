from pydantic import BaseModel, field_validator


MIN_SEARCH_QUERY_LENGTH = 2


class UserSearchQueryDTO(BaseModel):
    """Validated query params for user search endpoint."""

    q: str

    @field_validator("q")
    @classmethod
    def validate_q(cls, value: str) -> str:
        normalized_value = value.strip()
        if len(normalized_value) < MIN_SEARCH_QUERY_LENGTH:
            raise ValueError(
                f"Search query must be at least {MIN_SEARCH_QUERY_LENGTH} characters"
            )
        return normalized_value
