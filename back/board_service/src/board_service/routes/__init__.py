from .board_route import route as board_route
from .board_row_route import route as board_row_route
from .board_row_task_route import route as board_row_task_route
from .board_column_route import route as board_column_route
from .board_row_comment_route import route as board_row_comment_route
from .board_event_route import route as board_event_route
from .board_permission_route import route as board_permission_route
from .monitoring_route import route as monitoring_route

__all__ = [
	"board_route",
	"board_row_route",
	"board_row_task_route",
	"board_column_route",
	"board_row_comment_route",
	"board_event_route",
	"board_permission_route",
	"monitoring_route",
]

