from enum import StrEnum, auto


class TokenType(StrEnum):
    """
    Categorizes JSON Web Tokens to enforce strict security boundaries.

    This enumeration differentiates between short-lived credentials used
    for resource access and long-lived credentials used for session
    renewal. It prevents security vulnerabilities by ensuring a refresh
    token cannot be misused as an access token for protected API endpoints.
    """

    ACCESS = auto()
    REFRESH = auto()


class AvailabilityStatus(StrEnum):
    """
    Describes calendar availability states for housing inscriptions.

    This enumeration is used to expose day-by-day availability to clients.
    It distinguishes fully unavailable dates, already reserved dates, and
    dates currently free for new tenant offers.
    """

    NOT_AVAILABLE = "not_available"
    RESERVED = "reserved"
    AVAILABLE = "available"


class HealthStatus(StrEnum):
    """Enumeration of possible service availability states."""

    UP = auto()
    DOWN = auto()


class EnvMode(StrEnum):
    """
    Enumeration of supported application environment modes.

    Used to toggle environment-specific logic, such as database connection
    strings, logging levels, and security configurations.
    """

    DEV = auto()
    PROD = auto()


class UserRole(StrEnum):
    """ """

    USER = auto()
    ADMIN = auto()
