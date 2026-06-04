from enum import StrEnum, auto


class TokenType(StrEnum):
    """
    Categorize JSON Web Tokens to enforce strict security boundaries.

    :cvar ACCESS: Short-lived token used for resource access.
    :cvar REFRESH: Long-lived token used for session renewal.
    """

    ACCESS = auto()
    REFRESH = auto()


class AvailabilityStatus(StrEnum):
    """
    Describe calendar availability states for housing inscriptions.

    :cvar NOT_AVAILABLE: The date is fully unavailable.
    :cvar RESERVED: The date is already reserved by a tenant.
    :cvar AVAILABLE: The date is free for new tenant offers.
    """

    NOT_AVAILABLE = "not_available"
    RESERVED = "reserved"
    AVAILABLE = "available"


class HealthStatus(StrEnum):
    """
    Represent the possible service operational states.

    :cvar UP: The service is healthy and functional.
    :cvar DOWN: The service is experiencing issues or is offline.
    """

    UP = auto()
    DOWN = auto()


class EnvMode(StrEnum):
    """
    Define the supported application environment modes.

    :cvar DEV: Development mode for local testing and debugging.
    :cvar PROD: Production mode for live, secure deployment.
    """

    DEV = auto()
    PROD = auto()


class UserRole(StrEnum):
    """
    Define global system access levels for application users.

    :cvar USER: Standard user with regular access permissions.
    :cvar ADMIN: Administrator with full system control and management rights.
    """

    USER = auto()
    ADMIN = auto()


class UserRoleInBoard(StrEnum):
    """
    Define the collaboration roles a user can hold inside a specific board.

    :cvar OWNER: Full control over the board, including deletion and settings.
    :cvar EDITOR: Can modify board content, rows, and tasks.
    :cvar VIEWER: Read-only access to the board structure and tasks.
    """

    OWNER = auto()
    EDITOR = auto()
    VIEWER = auto()


class BoardColumnName(StrEnum):
    """
    Represent the standard column identifiers used within a project board.

    :cvar TASK_ID: Unique identifier column for tasks.
    :cvar TASK_NAME: Column showing the short summary or title of tasks.
    :cvar TASK_CONTENT: Column showing detailed description text for tasks.
    :cvar TASK_STATUS: Column tracking the completion status of tasks.
    :cvar COMMENT: Column dedicated to row discussions and comments.
    :cvar STARTING_FROM: Column indicating the start date of tasks.
    :cvar DEADLINE: Column indicating the target completion date.
    :cvar FILES: Column holding attachments and external documents.
    """

    TASK_ID = "TaskID"
    TASK_NAME = "TaskName"
    TASK_CONTENT = "TaskContent"
    TASK_STATUS = "TaskStatus"
    COMMENT = "Comment"
    STARTING_FROM = "StartingFrom"
    DEADLINE = "Deadline"
    FILES = "Files"


class BoardFieldType(StrEnum):
    """
    Specify the UI and data rendering formats allowed for board columns.

    :cvar TEXT: Small, single-line text input field.
    :cvar LONG_TEXT: Multi-line rich text field for detailed content.
    :cvar STATUS: Formatted field displaying lifecycle statuses.
    :cvar DATE: Date picker and calendar display field.
    :cvar FILE: File upload and download utility field.
    :cvar COMMENT: Dedicated thread interaction field for row discussions.
    :cvar SYSTEM: Automated field controlled exclusively by the application logic.
    """

    TEXT = "TEXT"
    LONG_TEXT = "LONG_TEXT"
    STATUS = "STATUS"
    DATE = "DATE"
    FILE = "FILE"
    COMMENT = "COMMENT"
    SYSTEM = "SYSTEM"


class BoardTaskStatus(StrEnum):
    """
    Represent the progression steps of a specific task within a board row.

    :cvar PENDING: Work is waiting to start or currently in progress.
    :cvar ACCEPTED: Task is approved or taken into consideration.
    :cvar COMPLETED: Work is finished successfully.
    """

    PENDING = auto()
    ACCEPTED = auto()
    COMPLETED = auto()
