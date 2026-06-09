from fastapi import FastAPI
from shared_models.models.server_settings import get_server_settings
from starlette.middleware.cors import CORSMiddleware

from board_service.routes import (
    board_route,
    board_row_route,
    monitoring_route,
    board_row_task_route,
    board_column_route,
    board_row_comment_route,
    board_event_route,
    board_permission_route,
)

SERVER_SETTINGS = get_server_settings()

app = FastAPI(
    title="Board Service",
    description="Service for managing Boards",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[SERVER_SETTINGS.front_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitoring_route)
app.include_router(board_route)
app.include_router(board_row_route)
app.include_router(board_row_task_route)
app.include_router(board_column_route)
app.include_router(board_row_comment_route)
app.include_router(board_event_route)
app.include_router(board_permission_route)
