from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from shared_models.enums import BoardTaskStatus

from .board_column_out_dto import BoardColumnOutDTO
from .user_dtos import UserOutDTO


class BoardRowTaskOutDTO(BaseModel):
    """
    Data transfer object representing an individual task cell for API output.

    :param id: Unique identifier of the task.
    :param board_row_id: ID of the row containing this task.
    :param board_column_id: ID of the specific column this task aligns with.
    :param board_column: Full outbound column structure details.
    :param task_name: Main summary title of the task.
    :param task_content: Body or technical description text of the task.
    :param task_status: Lifecycle processing state of the task.
    :param starting_from: Work commencement date.
    :param deadline: Hard target completion date.
    :param version: Concurrent modification tracking version.
    :param assigned_to_id: ID of the worker assigned to the task.
    :param assigned_to: Outbound details of the assignee.
    :param created_by_id: ID of the user who created the task.
    :param created_by: Outbound details of the task creator.
    :param created_at: Creation date and time.
    :param updated_at: Last modification date and time.
    """

    id: UUID

    board_row_id: UUID

    board_column_id: UUID
    board_column: BoardColumnOutDTO

    task_name: str
    task_content: str
    task_status: BoardTaskStatus
    starting_from: date
    deadline: date

    version: int

    assigned_to_id: UUID
    assigned_to: UserOutDTO
    created_by_id: UUID
    created_by: UserOutDTO

    created_at: datetime
    updated_at: datetime
