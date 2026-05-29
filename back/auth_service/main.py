from fastapi import FastAPI
from shared_models.models.server_settings import get_server_settings
from starlette.middleware.cors import CORSMiddleware

from auth_service.routes import monitoring_route, user_route, authentication_route

SERVER_SETTINGS = get_server_settings()

app = FastAPI(
    title="User Service",
    description="Service for managing user authentication and users",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[SERVER_SETTINGS.front_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitoring_route.route)
app.include_router(user_route.route)
app.include_router(authentication_route.route)
